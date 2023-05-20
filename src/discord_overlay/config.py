from typing import Any
from PyQt6.QtCore import QSettings

# App default settings
STATIC_DIR_NAME = "static"
IMAGES_DIR_NAME = "images"
QT_IMAGE_SEARCH_PATH = IMAGES_DIR_NAME
# StreamKit client id
DEFAULT_DISCORD_CLIENT_ID = '207646673902501888'
DEFAULT_DISCORD_ADDRESS = '127.0.0.1'
DEFAULT_DISCORD_PORT = '6463'
DEFAULT_STREAMKIT_ADDRESS = 'https://streamkit.discord.com'
DEFAULT_VOICE_CHANNEL_TYPE = 2


class Config(QSettings):
    def __init__(self, organization_domain: str, application_name: str) -> None:
        super().__init__(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            organization_domain,
            application_name,
        )
        self.set_default()

    def get(self, key: str, type: Any, default: Any = None) -> Any:
        return self.value(key, defaultValue=default, type=type)

    def set(self, key: str, value: Any, override: bool = True) -> None:
        setting = self.get(
            key,
            type=type(value)
        )
        if not setting or override:
            self.setValue(key, value)
        self.sync()

    def set_default(self) -> None:
        self.set('discord_client_address', DEFAULT_DISCORD_ADDRESS)
        self.set('discord_client_id', DEFAULT_DISCORD_CLIENT_ID)
        self.set('discord_client_port', DEFAULT_DISCORD_PORT)
        self.set('streamkit_address', DEFAULT_STREAMKIT_ADDRESS)
        self.set('voice_channel_type', DEFAULT_VOICE_CHANNEL_TYPE)
        self.sync()
