from typing import TYPE_CHECKING

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from PyQt6.QtGui import QMouseEvent

from .toggle_button import MainWindowHeaderToggleButtonWidget
from .title import MainWindowHeaderTitleWidget
from .status import MainWidgetHeaderConnStatusWidget

if TYPE_CHECKING:
    from .. import MainWidget


class MainWindowHeaderWidget(QWidget):
    def __init__(self, tooltip, main_widget: "MainWidget", parent) -> None:
        super().__init__(parent=parent)
        self.main_widget = main_widget
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet("""
            #MainWindowHeaderWidget{
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                background: #3c3c3c;
            }
        """)
        self.setFixedHeight(22)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip(tooltip)
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        sp_retain = self.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sp_retain)
        self.header_title = MainWindowHeaderTitleWidget(
            parent=self
        )
        self.header_conn_status = MainWidgetHeaderConnStatusWidget(
            controller=self.main_widget.controller,
            parent=self
        )
        self.header_toggle_button = MainWindowHeaderToggleButtonWidget(
            parent=self
        )
        self.layout().addWidget(self.header_title)
        self.layout().addWidget(
            self.header_conn_status,
            1,
            Qt.AlignmentFlag.AlignRight
        )
        self.layout().addWidget(
            self.header_toggle_button,
            0,
            Qt.AlignmentFlag.AlignRight
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.main_widget.old_pos = event.globalPosition().toPoint()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        delta = QPoint(event.globalPosition().toPoint() - self.main_widget.old_pos)
        pos_x = self.main_widget.x() + delta.x()
        pos_y = self.main_widget.y() + delta.y()
        self.main_widget.move(pos_x, pos_y)
        self.main_widget.old_pos = event.globalPosition().toPoint()
