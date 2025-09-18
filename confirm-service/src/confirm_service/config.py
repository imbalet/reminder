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

    TG_BOT_TOKEN: str
    TG_API_ADDRESS: str = ""

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    class Config:
        env_file = ".env"


config = Config()  # type: ignore
