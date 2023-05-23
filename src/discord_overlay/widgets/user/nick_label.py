from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from ...controller import Controller


class UserWidgetNickLabel(QLabel):
    def __init__(self, nickname, controller: Controller, parent=None) -> None:
        super().__init__(text=nickname, parent=parent)
        self.controller = controller
        self.setProperty("cssClass", "UserWidgetNickLabel")
        self.update_settings()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def update_settings(self) -> None:
        font_size = self.controller.config.get(
            "user_nickname_fontsize",
            type=int,
            default=12,
        )
        font_color = self.controller.config.get(
            "user_nickname_color",
            type=str,
            default="white",
        )
        self.setStyleSheet(f"""
            QLabel[cssClass="UserWidgetNickLabel"] {{
                color: {font_color};
                font-size: {font_size}px;
                padding-left: 2px;
            }}
        """)
