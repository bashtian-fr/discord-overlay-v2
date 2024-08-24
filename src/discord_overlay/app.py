import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from .config import Config
from .controller import Controller
from .model import Model
from .widgets.main import MainWidget
from .widgets.systemtray import SystemTrayWidget


class App(QApplication):
    def __init__(self, organization_domain: str, name: str) -> None:
        super().__init__([])
        self.setOrganizationDomain(organization_domain)
        self.setApplicationName(name)
        self.setQuitOnLastWindowClosed(False)
        self.setWindowIcon(QIcon("images:icon.png"))
        self.config = Config(organization_domain, name)
        self.model = Model()
        self.controller = Controller(model=self.model, config=self.config)
        self.controller.main_widget_visibility_hidden.connect(self.show_background_message)
        self.system_tray = SystemTrayWidget(
            controller=self.controller,
        )
        self.main_widget = MainWidget(
            controller=self.controller
        )
        self.main_widget.show()

    def show_background_message(self) -> None:
        if not self.system_tray.supportsMessages():
            logging.warning(
                "Overlay running in background."
                "This system doesnt support system notifications."
            )
            return

        if self.model.running_in_background_message_shown:
            # Only show the message once
            return

        self.model.running_in_background_message_shown = True
        self.system_tray.showMessage(
            self.applicationName(),
            f"The {self.applicationName()} is running in background",
            QIcon("images:icon.png"),
            msecs=1000
        )
