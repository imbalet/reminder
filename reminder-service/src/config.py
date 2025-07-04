from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    RMQ_ROUTING_KEY: str
    RMQ_USER: str
    RMQ_PASS: str
    RMQ_HOST: str
    RMQ_PORT: str

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def RMQ_URL(self) -> str:
        return (
            f"amqp://{self.RMQ_USER}:{self.RMQ_PASS}@{self.RMQ_HOST}:{self.RMQ_PORT}/"
        )

    class Config:
        env_file = ".env"


config = Config()  # type: ignore
