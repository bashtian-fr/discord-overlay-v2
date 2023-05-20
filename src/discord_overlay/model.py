import logging

from pathlib import Path
from PyQt6.QtCore import QDir, pyqtSignal, QObject

from .config import (
    STATIC_DIR_NAME,
    IMAGES_DIR_NAME,
    QT_IMAGE_SEARCH_PATH,
)


class Model(QObject):
    user_added_signal = pyqtSignal(dict)
    user_removed_signal = pyqtSignal(str)
    user_changed_signal = pyqtSignal(dict)
    users_emptied_signal = pyqtSignal()

    users = {}
    running_in_background_message_shown = False

    def __init__(self) -> None:
        super().__init__()
        self.basedir = Path(__file__).resolve()
        self.staticdir = Path(self.basedir) / ".." / STATIC_DIR_NAME
        self.imagedir = Path(self.staticdir) / IMAGES_DIR_NAME
        QDir.addSearchPath(QT_IMAGE_SEARCH_PATH, str(self.imagedir))

    def users_changed(self) -> None:
        logging.debug("Users have changed")

    def empty_users(self) -> None:
        logging.debug('Emptying users')
        self.users = {}
        self.users_changed()
        self.users_emptied_signal.emit()

    def add_user(self, user: dict) -> None:
        logging.debug('Adding user %s', user)
        self.users[user.get('id')] = user
        self.user_added_signal.emit(user)

    def delete_user(self, user_id: str) -> None:
        logging.debug('Deleting user %s', user_id)
        try:
            del self.users[user_id]
        except KeyError:
            logging.warning('User %s not found', user_id)

        self.users_changed()
        self.user_removed_signal.emit(user_id)

    def change_user(self, user: dict) -> None:
        self.user_changed_signal.emit(user)
