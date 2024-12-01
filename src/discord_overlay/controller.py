import logging
import sys
import traceback
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QErrorMessage

if TYPE_CHECKING:
    from .widgets.user import UserWidget

from .config import Config
from .libs import show_toast
from .libs.QDiscordWebSocket import QDiscordWebSocket
from .model import Model


class Controller(QObject):
    main_widget_visibility_hidden = pyqtSignal()
    main_widget_visibility_changed = pyqtSignal()
    settings_dialog_visibility_changed = pyqtSignal()
    settings_changed_signal = pyqtSignal(str)
    connection_status_changed = pyqtSignal(str)
    discord_connector = None

    def __init__(self, model: Model, config: Config) -> None:
        super().__init__()
        self.model = model
        self.config = config
        self.just_joined_channel = False
        self.init_discord_connector()

    @pyqtSlot()
    def quit_app(self) -> None:
        self.discord_connector.should_stop = True
        QApplication.instance().quit()

    def init_discord_connector(self) -> None:
        logging.info("Connecting to Discord...")
        self.discord_connector = QDiscordWebSocket(controller=self, parent=self)
        self.discord_connector.errorOccurred.connect(self.on_connection_error)
        self.discord_connector.custom_signal_connection_ok.connect(self.on_connection_ok)
        self.discord_connector.custom_signal_connection_failure.connect(self.on_connection_failure)
        self.discord_connector.open_()
        # self.discord_connector.custom_signal_you_joined_voice_channel.connect(
        #     self.on_you_joined_voice_channel_signal
        # )
        self.discord_connector.custom_signal_you_left_voice_channel.connect(
            self.on_you_left_voice_channel
        )
        self.discord_connector.custom_signal_update_voice_channel.connect(
            self.on_update_voice_channel
        )
        self.discord_connector.custom_signal_someone_left_voice_channel.connect(
            self.on_someone_left_channel
        )

    def on_connection_failure(self) -> None:
        self.connection_status_changed.emit("FAILURE")

    def on_connection_ok(self) -> None:
        self.connection_status_changed.emit("OK")

    def on_connection_error(self, error: str) -> None:
        self.connection_status_changed.emit("ERROR")
        logging.error("Unable to connect to discord - is discord running?")
        logging.error(f"{error}:\n{traceback.print_exc()}")
        error_dialog = QErrorMessage()
        error_dialog.setWindowTitle("Unable to connect to discord")
        error_dialog.showMessage(f"{error}. Is discord running?")
        error_dialog.exec()
        sys.exit(1)

    # def on_you_joined_voice_channel_signal(self) -> None:
    #     logging.debug("You joined a channel")

    def on_you_left_voice_channel(self) -> None:
        logging.debug(
            "Leaving channel: " f"{self.discord_connector.current_voice_channel_id}",
        )
        self.model.empty_users()

    def on_update_voice_channel(self, data: dict) -> None:
        logging.debug(f"Got an update channel event:\n {data}")
        user: dict = data["data"]["user"]
        user["nick"] = data["data"]["nick"]
        user["voice_state"] = data["data"]["voice_state"]

        if not user.get("id") in self.model.users:
            self.model.add_user(user)
        else:
            self.model.change_user(user)

    def on_someone_left_channel(self, data: dict) -> None:
        logging.debug(f"{data['data']['nick']} left the channel")
        user: dict = data["data"]["user"]
        self.model.delete_user(user.get("id"))

    def someone_left_channel_notification(
        self, user_widget: "UserWidget", send_toast=True
    ) -> None:
        icon = self.get_icon(user_widget.avatar_data, user_widget.get_avatar_size())
        logging.debug(f"{user_widget.user_data['nick']} left the channel")

        if user_widget.user_data.get("id") == self.discord_connector.user.get("id"):
            return

        if send_toast:
            show_toast(
                parent=None,
                title="Someone left the channel",
                text=f"{user_widget.user_data['nick']} left the channel",
                # preset="error",
                icon=icon,
            )

    def someone_joined_channel_notification(self, user_widget: "UserWidget") -> None:
        logging.debug(f"{user_widget.user_data['nick']} joined the channel")
        if self.just_joined_channel:
            self.just_joined_channel = False
            return

        if user_widget.user_data.get("id") == self.discord_connector.user.get("id"):
            return

        icon = self.get_icon(user_widget.avatar_data, user_widget.get_avatar_size())

        show_toast(
            parent=None,
            title="Discord-Overlay",
            text=f"{user_widget.user_data['nick']} joined the channel",
            # preset="success",
            icon=icon,
        )

    def get_icon(self, bytes, size):
        icon_pix = QPixmap()
        icon_pix.loadFromData(bytes)
        icon_pix = icon_pix.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        return icon_pix
