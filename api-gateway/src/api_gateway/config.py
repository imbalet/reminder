from enum import Enum

from pydantic_settings import BaseSettings


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

    class Config:
        env_file = ".env"


config = Config()  # type: ignore
