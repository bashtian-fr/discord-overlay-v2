import logging
import urllib3

from PyQt6.QtCore import (
    QThread,
    Qt,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
)
from PyQt6.QtGui import QPixmap

from ...controller import Controller
from .avatar import RoundUserWidgetAvatar
from .nick_label import UserWidgetNickLabel


class UserWidget(QWidget):
    def __init__(self, controller: Controller, user_data, parent=None) -> None:
        super().__init__(parent=parent)
        self.controller = controller
        self.controller.discord_connector.custom_signal_speaking_start.connect(
            self.start_speaking
        )
        self.controller.discord_connector.custom_signal_speaking_stop.connect(
            self.stop_speaking
        )

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setObjectName(f"user_widget_{user_data['id']}")
        self.avatar_data = None
        self.avatar_label = None
        self.deafened = False
        self.muted = False
        self.user_data = user_data

        self.init_ui()
        self.update_user_icons()
        self.set_avatar()

        if self.get_show_only_speakers():
            self.hide()
        else:
            self.show()

    def init_ui(self) -> None:
        layout = QGridLayout()
        layout.setContentsMargins(4, 4, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Nickname
        self.nick_label = UserWidgetNickLabel(
            self.user_data["nick"],
            controller=self.controller,
            parent=self,
        )

        # Avatar container
        self.avatar_container = QLabel(self)
        container_layout = QGridLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        self.avatar_container.setLayout(container_layout)

        # Avatar border
        min_width = self.get_avatar_size()+(self.get_speaker_border_size()*2)
        min_height = min_width
        self.avatar_label_border_round = QLabel(self)
        size_policy = self.avatar_label_border_round.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.avatar_label_border_round.setSizePolicy(size_policy)
        self.avatar_label_border_round.hide()
        self.avatar_label_border_round.setFixedSize(min_width, min_height)

        self.set_deafen_icon()
        self.set_mute_icon()
        self.layout().addWidget(self.avatar_label_border_round, 0, 0)
        self.layout().addWidget(self.avatar_container, 0, 0)
        self.layout().addWidget(self.nick_label, 0, 1)

    def set_mute_icon(self) -> None:
        mute_pixmap = QPixmap("images:muted.png")
        self.mute_icon = QLabel(
            parent=self
        )
        self.mute_icon.hide()
        self.mute_icon.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.mute_icon.setObjectName("mute_user")
        self.mute_icon.setPixmap(
            mute_pixmap.scaled(
                20, 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )
        self.mute_icon.setFixedSize(20, 20)
        self.layout().addWidget(self.mute_icon, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

    def set_deafen_icon(self) -> None:
        deaf_pixmap = QPixmap("images:deafen.png")
        self.deafen_icon = QLabel(
            parent=self
        )
        self.deafen_icon.hide()
        self.deafen_icon.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.deafen_icon.setObjectName("deaf_user")
        self.deafen_icon.setPixmap(
            deaf_pixmap.scaled(
                20, 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )
        self.deafen_icon.setFixedSize(20, 20)
        self.layout().addWidget(self.deafen_icon, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

    def get_show_only_speakers(self) -> bool:
        return self.controller.config.get(
            "show_only_speakers",
            default=False,
            type=bool
        )

    def get_avatar_size(self) -> int:
        return self.controller.config.get(
            "user_avatar_size",
            default=28,
            type=int
        )

    def get_speaker_border_size(self) -> int:
        return 3

    def update_setting(self, setting_name: str) -> None:
        if "nickname" in setting_name:
            return self.nick_label.update_settings()

        if "user_avatar_size" in setting_name:
            return self.set_avatar_data(self.avatar_data)

        if "speaker_border_color":
            return self.set_avatar_label_border_round()

        logging.error(f"Unsuported setting: {setting_name}")

    def set_avatar_label_border_round(self) -> None:
        border_color = self.controller.config.get(
            "speaker_border_color",
            default="green",
            type=str
        )
        self.avatar_label_border_round.setFixedSize(
            self.get_avatar_size()+(self.get_speaker_border_size()*2),
            self.get_avatar_size()+(self.get_speaker_border_size()*2)
        )
        self.avatar_label_border_round.setStyleSheet(
            f"border: {self.get_speaker_border_size()}px solid {border_color};"
            f"border-radius: {int(self.get_avatar_size()/2)+self.get_speaker_border_size()}px;")

    def update_avatar(self) -> None:
        self.avatar_label.setParent(None)
        self.set_avatar()

    def set_avatar(self) -> None:
        identifier = self.user_data.get("id")
        avatar = self.user_data.get("avatar")
        self.avatar_url = f"https://cdn.discordapp.com/avatars/{identifier}/{avatar}.png"

        if not avatar:
            # That is how discord do it
            avatar_id = int(self.user_data.get("discriminator")) % 5
            self.avatar_url = f"https://cdn.discordapp.com/embed/avatars/{avatar_id}.png"

        # Run a thread with the object and set avatar
        self.thread = UrlThreadClass(
            url=self.avatar_url,
            parent=self,
        )
        self.thread.start()
        self.thread.any_signal.connect(self.set_avatar_data)

    def set_avatar_data(self, avatar_data: bytes) -> None:
        self.avatar_data = avatar_data

        if self.avatar_label:
            self.avatar_label.setParent(None)

        self.avatar_label = RoundUserWidgetAvatar(
            user_id=self.user_data['id'],
            avatar=self.avatar_data,
            controller=self.controller,
            parent=self
        )

        self.set_avatar_label_border_round()
        self.layout().addWidget(self.avatar_label_border_round, 0, 0)
        self.avatar_container.layout().addWidget(self.avatar_label, 0, 0)

    def update_data(self, user_data, auto_update=True) -> None:
        self.user_data = user_data
        if auto_update:
            self.update_user_icons()

    def stop_speaking(self, data):
        if data["data"]["user_id"] != self.user_data["id"]:
            return

        self.avatar_label_border_round.hide()

        if self.controller.config.get(
            "show_only_speakers",
            default=False,
            type=bool
        ):
            self.hide()

    def start_speaking(self, data):
        if data["data"]["user_id"] != self.user_data["id"]:
            return
        self.avatar_label_border_round.show()
        self.show()

    def is_user_deafen(self):
        if self.user_data["voice_state"]["deaf"] \
                or self.user_data["voice_state"]["self_deaf"]:
            return True
        return False

    def is_user_mute(self):
        if (self.user_data["voice_state"]["mute"]
                or self.user_data["voice_state"]["self_mute"]) \
                    and not self.is_user_deafen():
            return True
        return False

    def update_user_icons(self):
        if self.is_user_deafen():
            self.mute_icon.hide()
            self.deafen_icon.show()

        if self.is_user_mute():
            self.deafen_icon.hide()
            self.mute_icon.show()

        if not self.is_user_mute():
            self.mute_icon.hide()

        if not self.is_user_deafen():
            self.deafen_icon.hide()

    def toggle(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()


class UrlThreadClass(QThread):

    any_signal = pyqtSignal("QByteArray")

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.is_running = True

    def run(self):
        http = urllib3.PoolManager()
        response = http.request("GET", self.url)
        self.any_signal.emit(response.data)

    def stop(self):
        self.is_running = False
        self.terminate()
