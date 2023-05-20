from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout


class CentralWidget(QFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.setObjectName(self.__class__.__name__)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
