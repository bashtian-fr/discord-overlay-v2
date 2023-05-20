from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QMouseEvent


class MainWindowHeaderToggleButtonWidget(QPushButton):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.setObjectName(self.__class__.__name__)
        self.setToolTip("Hide the frame")
        self.init_ui()

    def init_ui(self) -> None:
        self.setStyleSheet("""
            #MainWindowHeaderToggleButtonWidget {
                border-image: url(images:hide.png);
                background-repeat: no-repeat;
                width: 16px;
                height: 16px;
                padding: 2px;
                margin: 2px;
            }
            #MainWindowHeaderToggleButtonWidget:hover {
                background-color: #585858;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # implement mouseMoveEvent to override parent one
        # in order to avoid setting position when clicking button
        pass
