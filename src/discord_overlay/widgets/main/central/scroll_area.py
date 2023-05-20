import logging

from PyQt6.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout

from ...user import UserWidget
from ....controller import Controller


class CentralWidgetScrollArea(QScrollArea):
    def __init__(self, controller: Controller, parent=None) -> None:
        super().__init__(parent=parent)
        self.controller = controller
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet("""
            #CentralWidgetScrollArea {
                background: transparent;
                border: none;
                border-left: 1px dotted rgba(255,255,255, 0.5);
                border-right: 1px dotted rgba(255,255,255, 0.5);
            }
        """)
        self.setWidgetResizable(True)
        self.init_ui()

    def init_ui(self) -> None:
        self.user_container = ScrollAreaUserContainer(
            controller=self.controller,
            parent=self
        )
        self.setWidget(self.user_container)

    def hide_border(self) -> None:
        self.setStyleSheet("""
            #CentralWidgetScrollArea {
                background: transparent;
                border: none;
            }
        """)

    def show_border(self) -> None:
        self.setStyleSheet("""
            #CentralWidgetScrollArea {
                background: transparent;
                border: none;
                border-left: 1px dotted rgba(255,255,255, 0.5);
                border-right: 1px dotted rgba(255,255,255, 0.5);
            }
        """)


class ScrollAreaUserContainer(QWidget):
    toggle_widgets_signal = pyqtSignal()

    def __init__(self, controller: Controller, parent) -> None:
        super().__init__(parent=parent)
        self.controller = controller
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet("""
            #ScrollAreaUserContainer {
                background: transparent;
            }
        """)
        self.controller.settings_changed_signal.connect(self.on_settings_changed)
        self.controller.model.users_emptied_signal.connect(self.on_users_emptied)
        self.controller.model.user_added_signal.connect(self.on_user_added)
        self.controller.model.user_removed_signal.connect(self.on_user_removed)
        self.controller.model.user_changed_signal.connect(self.on_user_change)
        self.threadpool = QThreadPool(self)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setDirection(QVBoxLayout.Direction.BottomToTop)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def on_user_change(self, user_data: dict) -> None:
        user_widget = self.get_user_widget(user_data.get("id"))
        user_widget.update_data(user_data)

    def get_user_widget(self, user_id) -> UserWidget:
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget.user_data.get("id") == user_id:
                return widget

    def on_settings_changed(self, setting_name: str) -> None:
        if setting_name == "show_only_speakers":
            return self.toggle_widgets_signal.emit()

        if setting_name.startswith("user_") or setting_name.startswith("speaker_"):
            for i in reversed(range(self.layout().count())):
                widget: UserWidget = self.layout().itemAt(i).widget()
                widget.update_setting(setting_name)

    def add_user(self, user) -> None:
        user_widget = UserWidget(
            controller=self.controller,
            user_data=user,
            parent=self,
        )
        self.toggle_widgets_signal.connect(user_widget.toggle)
        self.layout().addWidget(user_widget)

    def on_users_emptied(self) -> None:
        self.remove_users()

    def on_user_added(self, user: dict) -> None:
        logging.debug(f"Adding user to UI {user}")
        self.add_user(user)

    def on_user_removed(self, user_id: str) -> None:
        self.remove_users(user_id=user_id)

    def remove_users(self, user_id: str = None) -> None:
        logging.debug(f"Removing users: {user_id}")
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if not user_id or widget.user_data.get("id") == user_id:
                self.layout().removeWidget(widget)
                if widget:
                    widget.setParent(None)
        logging.debug("Finished removing user")
