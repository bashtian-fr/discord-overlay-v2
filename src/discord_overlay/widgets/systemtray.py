from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

from ..controller import Controller


class SystemTrayWidget(QSystemTrayIcon):
    def __init__(self, controller: Controller) -> None:
        super().__init__()
        self.controller = controller
        self._ui = SystemTrayWidgetUi()
        self._ui.setup_ui(self, self.controller.config.applicationName())

        self._ui.toggle_overlay_action.triggered.connect(
            self.controller.main_widget_visibility_changed.emit
        )
        self._ui.settings_action.triggered.connect(
            self.controller.settings_dialog_visibility_changed.emit
        )
        self._ui.quit_action.triggered.connect(self.controller.quit_app)
        self.activated.connect(self.on_activated)

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason.value == QSystemTrayIcon.ActivationReason.Trigger.value:
            self.controller.main_widget_visibility_changed.emit()


class SystemTrayWidgetUi():
    def setup_ui(self, system_tray: SystemTrayWidget, application_name: str) -> None:
        system_tray.setToolTip(application_name)
        system_tray.setIcon(QIcon('images:icon.png'))
        system_tray.setVisible(True)

        self.menu = QMenu()
        self.toggle_overlay_action = \
            QAction('&Toggle the overlay', parent=self.menu)
        self.settings_action = QAction('&Settings', parent=self.menu)
        self.quit_action = QAction('&Exit', parent=self.menu)

        self.menu.addAction(self.toggle_overlay_action)
        self.menu.addAction(self.settings_action)
        self.menu.addAction(self.quit_action)

        system_tray.setContextMenu(self.menu)
