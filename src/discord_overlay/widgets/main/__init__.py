from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon

from .central import CentralWidget
from .central.scroll_area import CentralWidgetScrollArea
from .footer import MainWindowFooter
from .header import MainWindowHeaderWidget
from ..settings import SettingsDialog
from ...controller import Controller


class MainWidget(QMainWindow):
    def __init__(self, controller: Controller) -> None:
        super().__init__()
        self.controller = controller
        self._ui = MainWidgetUi()
        self._ui.setup_ui(self)
        self.old_pos = self.pos()
        self.setWindowIcon(QIcon("images:icon.png"))
        self._ui.header.header_toggle_button.clicked.connect(self.toggle)
        self.controller.main_widget_visibility_changed.connect(self.toggle)
        self.controller.settings_dialog_visibility_changed.connect(
            self.toggle_settings
        )

    def toggle(self) -> None:
        if self.is_visible() or self._ui.header.isVisible():
            self.make_not_visible()
        else:
            self.make_visible()

    def make_not_visible(self) -> None:
        self.controller.config.set("is_visible", False)
        self._ui.header.hide()
        self._ui.scroll_area.hide_border()
        self._ui.footer.hide()
        self.controller.main_widget_visibility_hidden.emit()

    def make_visible(self) -> None:
        self.controller.config.set("is_visible", True)
        self._ui.header.show()
        self._ui.scroll_area.show_border()
        self._ui.footer.show()

    def toggle_settings(self) -> None:
        if self._ui.settings_dialog.isVisible():
            self._ui.settings_dialog.hide()
        else:
            self._ui.settings_dialog.show()

    def is_visible(self) -> bool:
        is_visible = self.controller.config.get("is_visible", type=bool, default=True)
        return is_visible


class MainWidgetUi:
    def setup_ui(self, main_widget: MainWidget) -> None:
        self.main_widget = main_widget
        self.set_attributes()
        self.set_dialog()
        self.set_central_widget()
        self.set_header()
        self.set_scroll_area()
        self.set_footer()

    def set_attributes(self) -> None:
        self.main_widget.setAttribute(
            Qt.WidgetAttribute.WA_AlwaysShowToolTips)
        self.main_widget.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_widget.setAttribute(
            Qt.WidgetAttribute.WA_NoSystemBackground)
        self.main_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            # Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint)
        self.main_widget.setMinimumHeight(300)
        self.main_widget.setMinimumWidth(300)
        self.main_widget.setGeometry(0, 0, 400, 500)
        self.main_widget.move(QPoint(20, 20))

    def set_dialog(self) -> None:
        self.settings_dialog = SettingsDialog(
            controller=self.main_widget.controller,
            parent=self.main_widget
        )

    def set_central_widget(self) -> None:
        self.centralwidget = CentralWidget(parent=self.main_widget)
        self.main_widget.setCentralWidget(self.centralwidget)

    def set_header(self) -> None:
        self.header = MainWindowHeaderWidget(
            tooltip="Hold left click to move",
            main_widget=self.main_widget,
            parent=self.centralwidget,
        )
        self.centralwidget.layout().addWidget(self.header)

    def set_scroll_area(self) -> None:
        self.scroll_area = CentralWidgetScrollArea(
            controller=self.main_widget.controller,
            parent=self.centralwidget
        )

        self.centralwidget.layout().addWidget(self.scroll_area)

    def set_footer(self) -> None:
        self.footer = MainWindowFooter(parent=self.centralwidget)
        self.centralwidget.layout().addWidget(self.footer)
