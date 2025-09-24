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

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    RMQ_DLQ_FAILED_REMINDERS_NAME: str
    RMQ_DLX_FAILED_REMINDERS_NAME: str
    RMQ_USER_ADD_QUEUE: str
    RMQ_DELIVERY_METHOD_ADD_QUEUE: str
    RMQ_DELIVERY_METHOD_REMOVE_QUEUE: str
    RMQ_REMINDER_DEACTIVATE_QUEUE: str
    RMQ_USER: str
    RMQ_PASS: str
    RMQ_HOST: str
    RMQ_PORT: str

    @property
    def RMQ_URL(self) -> str:
        return (
            f"amqp://{self.RMQ_USER}:{self.RMQ_PASS}@{self.RMQ_HOST}:{self.RMQ_PORT}/"
        )

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


config = Config()  # type: ignore
