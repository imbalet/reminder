from enum import Enum
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevels(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Config(BaseSettings):
    LOG_LEVEL: LogLevels
    AUTH_URL: str
    REMINDER_URL: str
    USER_URL: str
    JWKS_ENDPOINT: str

    @property
    def JWKS_URL(self):
        return f"{self.AUTH_URL}{self.JWKS_ENDPOINT}"

    model_config = SettingsConfigDict(env_file=".env")


_config_instance: Config | None = None


def _get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()  # type: ignore
    return _config_instance


class _ConfigProxy:
    def __getattr__(self, name):
        return getattr(_get_config(), name)

    def __setattr__(self, name, value):
        setattr(_get_config(), name, value)


if TYPE_CHECKING:
    config: Config
else:
    config = _ConfigProxy()
