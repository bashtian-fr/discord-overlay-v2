from PyQt6.QtCore import QPropertyAnimation, Qt
from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect

from ....controller import Controller


class MainWidgetHeaderConnStatusWidget(QLabel):
    def __init__(self, controller: Controller, parent) -> None:
        super().__init__(parent=parent)
        self.controller = controller
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet("""
            #MainWidgetHeaderConnStatusWidget {
                background-color: red;
                border-radius: 7px;
            }
        """)
        self.setToolTip("Connecting...")
        self.setFixedSize(14, 14)
        self.controller.connection_status_changed.connect(self.on_status_changed)

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(1000)
        self.anim.setLoopCount(-1)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)

        self.show()
        self.anim.start()

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def on_status_changed(self, status: str) -> None:
        if status in ["FAILURE", "ERROR"]:
            self.setToolTip("Failing to connect")
            self.anim.start()
            self.set_background_color('red')

        if status == "OK":
            self.setToolTip("Connected")
            self.set_background_color('green')
            self.anim.stop()

    def set_background_color(self, color) -> None:
        self.setStyleSheet("""
            #MainWidgetHeaderConnStatusWidget {
                background-color: %s;
                border-radius: 7px;
            }
        """ % color)
