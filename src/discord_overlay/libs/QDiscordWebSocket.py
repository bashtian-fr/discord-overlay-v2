import json
import logging
import sys
import uuid
from typing import TYPE_CHECKING

import requests
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWebSockets import QWebSocket

if TYPE_CHECKING:
    from ..controller import Controller


class QDiscordWebSocket(QWebSocket):
    custom_signal_you_joined_voice_channel = pyqtSignal()
    custom_signal_you_left_voice_channel = pyqtSignal()
    custom_signal_someone_left_voice_channel = pyqtSignal(dict)
    custom_signal_someone_joined_voice_channel = pyqtSignal(dict)
    custom_signal_update_voice_channel = pyqtSignal(dict)
    custom_signal_speaking_start = pyqtSignal(dict)
    custom_signal_speaking_stop = pyqtSignal(dict)

    custom_signal_authenticated = pyqtSignal()

    custom_signal_connection_error = pyqtSignal(str)
    custom_signal_connection_failure = pyqtSignal()
    custom_signal_connection_ok = pyqtSignal()

    def __init__(self, controller: "Controller", parent=None) -> None:
        self.controller = controller
        self.client_id = self.controller.config.get("discord_client_id", type=str)
        self._origin = self.controller.config.get("streamkit_address", type=str)
        self.address = self.controller.config.get("discord_client_address", type=str)
        self.port = self.controller.config.get("discord_client_port", type=str)
        self.voice_channel_type = self.controller.config.get("voice_channel_type", type=int)
        self.uri = f"ws://{self.address}:{self.port}/?v=1&client_id={self.client_id}"

        self.access_token = None
        self.user = None
        self.in_room = []
        self.current_voice_channel_id = None
        self.guilds = {}
        self.channels = {}
        self.userlist = {}
        self.last_connection = None
        self.authenticated = False

        super().__init__(origin=self._origin, parent=parent)

        self.textMessageReceived.connect(self.on_message)
        self.supported_commands = [
            "DISPATCH",
            "AUTHENTICATE",
            "AUTHORIZE",
            "GET_GUILDS",
            "GET_CHANNELS",
            "GET_CHANNEL",
            "SUBSCRIBE",
            "UNSUBSCRIBE",
            "GET_SELECTED_VOICE_CHANNEL",
        ]
        self.supported_events = [
            "READY",
            "VOICE_STATE_UPDATE",
            "VOICE_CONNECTION_STATUS",
            "VOICE_CHANNEL_SELECT",
            "SPEAKING_START",
            "SPEAKING_STOP",
            "VOICE_STATE_CREATE",
            "VOICE_STATE_DELETE",
        ]

    def open_(self) -> None:
        self.open(QUrl(self.uri))

    def on_message(self, message: str) -> None:
        data: dict = json.loads(message)
        command = data.get("cmd")

        if data.get("evt") == "ERROR":
            self.handle_error(data)

        if command not in self.supported_commands:
            logging.warning(f"Unsupported command: {command}")
            return

        if command == "DISPATCH":
            self.handle_dispatch_command(data)
            return

        if command == "AUTHENTICATE":
            self.handle_authenticate_command(data)
            return

        if command == "AUTHORIZE":
            self.handle_authorize_command(data)
            return

        if command == "GET_CHANNEL":
            self.handle_get_channel(data)
            return

        if command == "GET_SELECTED_VOICE_CHANNEL":
            self.handle_get_selected_voice_channel(data)
            return

    def handle_error(self, data: dict) -> None:
        code = data.get("data", {}).get("code")
        if code == 4009:
            return

        message = data.get("data", {}).get("message", "Unknown error")
        logging.error(f"An error happened: ({code}) {message}")
        logging.error(f"data:\n{json.dumps(data, indent=4)}")
        sys.exit(1)

    def handle_get_channel(self, data: dict) -> None:
        if data["data"]["type"] == self.voice_channel_type:
            # We already are in a voice channel
            if self.current_voice_channel_id:
                self.set_active_channel(None)

            self.controller.just_joined_channel = True
            self.set_active_channel(data["data"]["id"], name=data["data"]["name"])
        else:
            logging.error(f"Unsupported channel type: {data['data']['type']}")

    def handle_get_selected_voice_channel(self, data: dict) -> None:
        if not data["data"]:
            logging.info("We are not connected to any voice channel yet")
            return
        else:
            if data["data"].get("name"):
                logging.info(f"Already in a channel: {data['data'].get("name")}")
                self.set_active_channel(data["data"]["id"], name=data["data"]["name"])

    def handle_dispatch_command(self, data: dict) -> None:
        event = data["evt"]
        if event not in self.supported_events:
            logging.warning(f"Unsupported event:{event}")
            return

        if event == "READY":
            # We got server info, lets authenticate
            self.request_authentication_token()
            return

        if event == "VOICE_STATE_DELETE":
            # You or A user leaves a subscribed voice channel
            logging.debug(
                f"Someone left a channel: {data['data']['user']['id']}"
                f"({data['data']['user']['username']})"
            )
            self.custom_signal_someone_left_voice_channel.emit(data)
            if data["data"]["user"]["id"] == self.user["id"]:
                self.set_active_channel(None)
            return

        if event == "VOICE_STATE_UPDATE":
            # A user's voice state changes in a subscribed voice channel (mute, volume, etc.)
            logging.debug(
                f"Voice state update: {data['data']['user']['id']}"
                f"({data['data']['user']['username']})"
            )
            self.custom_signal_update_voice_channel.emit(data)
            return

        if event == "VOICE_CHANNEL_SELECT":
            # We join or leave a channel
            # When we leave we need to unsubscribe from previous channel
            channel_id = data.get("data", {}).get("channel_id")

            if not channel_id:
                # we leave the channel
                self.set_active_channel(None)
                return

            # We join a channel, request channel details which handles
            # setting the active channel in handle_get_channel
            self.request_channel_details(channel_id)
            return

        if event == "VOICE_STATE_CREATE":
            # A user joins a subscribed voice channel
            # self.custom_signal_someone_joined_voice_channel.emit(data)
            return

        if event == "VOICE_CONNECTION_STATUS":
            # The client's voice connection status changes
            self.last_connection = data["data"]["state"]
            return

        if event == "SPEAKING_START":
            self.custom_signal_speaking_start.emit(data)
            return

        if event == "SPEAKING_STOP":
            self.custom_signal_speaking_stop.emit(data)
            return

    def handle_authenticate_command(self, data: dict) -> None:
        event = data["evt"]
        if event == "ERROR":
            logging.info("Authenticating...")
            self.get_access_token_stage1()
        else:
            self.custom_signal_connection_ok.emit()
            self.user: dict = data["data"]["user"]
            logging.info(f"Authenticated as {self.user.get('username')} ({self.user.get('id')})")
            self.authenticated = True
            self.custom_signal_authenticated.emit()
            self.sub_server()
            self.request_find_user()

    def handle_authorize_command(self, data: dict) -> None:
        self.get_access_token_stage2(data["data"]["code"])

    def set_active_channel(self, channel_id, name=None) -> None:
        if not channel_id:
            logging.info("You left the voice channel")
            if self.current_voice_channel_id:
                self.unsub_voice_channel(self.current_voice_channel_id)
                self.custom_signal_you_left_voice_channel.emit()
                self.current_voice_channel_id = None
            return

        logging.info(
            f"You join a new channel: {name or 'UnknownName'} ({channel_id})",
        )
        if self.current_voice_channel_id:
            # First unsubscribe from the current channel
            self.unsub_voice_channel(self.current_voice_channel_id)

        # Then subscribe to the new channel
        self.current_voice_channel_id = channel_id
        self.sub_voice_channel(channel_id)
        # self.custom_signal_you_joined_voice_channel.emit()

    def sub_raw(self, event, args, nonce) -> None:
        if not nonce:
            nonce = uuid.uuid4()

        logging.debug(f"Emitting SUBSCRIBE with params: {args}, {event}, {nonce}")

        cmd = {"cmd": "SUBSCRIBE", "args": args, "evt": event, "nonce": f"{nonce}"}
        self.sendTextMessage(json.dumps(cmd))

    def unsub_raw(self, event, args, nonce) -> None:
        if not nonce:
            nonce = uuid.uuid4()

        logging.debug(f"Emitting UNSUBSCRIBE with params: {args}, {event}, {nonce}")

        cmd = {"cmd": "UNSUBSCRIBE", "args": args, "evt": event, "nonce": f"{nonce}"}
        self.sendTextMessage(json.dumps(cmd))

    def sub_server(self) -> None:
        self.sub_raw("VOICE_CHANNEL_SELECT", None, None)
        self.sub_raw("VOICE_CONNECTION_STATUS", None, None)

    def sub_channel(self, event, channel_id) -> None:
        self.sub_raw(event, {"channel_id": channel_id}, None)

    def unsub_channel(self, event, channel_id) -> None:
        self.unsub_raw(event, {"channel_id": channel_id}, None)

    def unsub_voice_channel(self, channel_id) -> None:
        self.unsub_channel("VOICE_STATE_CREATE", channel_id)
        self.unsub_channel("VOICE_STATE_UPDATE", channel_id)
        self.unsub_channel("VOICE_STATE_DELETE", channel_id)
        self.unsub_channel("SPEAKING_START", channel_id)
        self.unsub_channel("SPEAKING_STOP", channel_id)

    def sub_voice_channel(self, channel_id) -> None:
        self.sub_channel("VOICE_STATE_CREATE", channel_id)
        self.sub_channel("VOICE_STATE_UPDATE", channel_id)
        self.sub_channel("VOICE_STATE_DELETE", channel_id)
        self.sub_channel("SPEAKING_START", channel_id)
        self.sub_channel("SPEAKING_STOP", channel_id)

    def get_access_token_stage1(self) -> None:
        logging.debug("Emitting AUTHORIZE")
        cmd = {
            "cmd": "AUTHORIZE",
            "args": {
                "client_id": self.client_id,
                "scopes": ["rpc", "messages.read"],
                "prompt": "none",
            },
            "nonce": "deadbeef",
        }
        self.sendTextMessage(json.dumps(cmd))

    def get_access_token_stage2(self, code1) -> None:
        url = "https://streamkit.discord.com/overlay/token"
        myobj = {"code": code1}
        response = requests.post(url, json=myobj, timeout=30)

        try:
            jsonresponse = json.loads(response.text)
        except json.JSONDecodeError:
            jsonresponse = {}

        if "access_token" in jsonresponse:
            self.access_token = jsonresponse["access_token"]
            self.request_authentication_token()
        else:
            sys.exit(1)

    def request_authentication_token(self) -> None:
        logging.debug("Emitting AUTHENTICATE")
        cmd = {
            "cmd": "AUTHENTICATE",
            "args": {"access_token": self.access_token},
            "nonce": "deadbeef",
        }
        self.sendTextMessage(json.dumps(cmd))

    def request_find_user(self) -> None:
        logging.debug("Emitting GET_SELECTED_VOICE_CHANNEL")
        cmd = {"cmd": "GET_SELECTED_VOICE_CHANNEL", "args": {}, "nonce": "deadbeef"}
        self.sendTextMessage(json.dumps(cmd))

    def request_channel_details(self, channel_id) -> None:
        logging.debug(f"Emitting GET_CHANNEL for {channel_id}")
        cmd = {"cmd": "GET_CHANNEL", "args": {"channel_id": channel_id}, "nonce": channel_id}
        self.sendTextMessage(json.dumps(cmd))
