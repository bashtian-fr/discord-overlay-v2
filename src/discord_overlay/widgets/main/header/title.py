from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QIcon


class MainWindowHeaderTitleWidget(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet("""
            #MainWindowHeaderTitleWidget {
                padding-left: 5px;
            }
        """)
        self.setPixmap(QIcon("images:title.png").pixmap(100, 20))
