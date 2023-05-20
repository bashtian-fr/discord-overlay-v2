from PyQt6.QtWidgets import QSizeGrip


class MainWindowFooterSizeGripWidget(QSizeGrip):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setToolTip("Hold left click to resize")
