from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from .size_grip import MainWindowFooterSizeGripWidget


class MainWindowFooter(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet("""
            #MainWindowFooter {
                background: #007acc;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setup_ui()

    def setup_ui(self) -> None:
        sp_retain = self.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sp_retain)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.header_resize_grip = MainWindowFooterSizeGripWidget(
            parent=self
        )
        self.layout().addWidget(
            self.header_resize_grip,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )
