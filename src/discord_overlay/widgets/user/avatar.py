from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import (
    QBrush,
    QPainter,
    QPixmap,
    QColorConstants,
)

from ...controller import Controller


class UserWidgetAvatar(QLabel):
    def __init__(self, user_id: str, avatar: bytes, controller: Controller, parent=None) -> None:
        super().__init__(parent=parent)
        self.setObjectName(f"{self.__class__.__name__}_{user_id}")
        self.user_id = user_id
        self.controller = controller
        self.avatar_bytes = avatar
        self.avatar_size = self.controller.config.get(
            "user_avatar_size",
            default=28,
            type=int
        )
        self.setFixedSize(self.avatar_size, self.avatar_size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.avatar_pix = QPixmap()

        self.avatar_pix.loadFromData(self.avatar_bytes)
        self.avatar_pix = self.avatar_pix.scaled(
            self.avatar_size,
            self.avatar_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )


class RoundUserWidgetAvatar(UserWidgetAvatar):
    def __init__(self, user_id: str, avatar: bytes, controller: Controller, parent=None) -> None:
        super().__init__(user_id=user_id, avatar=avatar, controller=controller, parent=parent)

    def paintEvent(self, event=None) -> None:
        brush = QBrush(QColorConstants.Transparent, self.avatar_pix)
        painter = QPainter(self)
        painter.setPen(QColorConstants.Transparent)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(brush)
        painter.drawEllipse(
            0,
            0,
            self.width(),
            self.height(),
        )
        self.setPixmap(self.avatar_pix)


class SquareUserWidgetAvatar(UserWidgetAvatar):
    def __init__(self, user_id: str, avatar: bytes, controller: Controller, parent=None) -> None:
        super().__init__(user_id=user_id, avatar=avatar, controller=controller, parent=parent)
        self.setPixmap(self.avatar_pix)
