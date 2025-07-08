from pydantic_settings import BaseSettings


class Config(BaseSettings):
    TG_BOT_TOKEN: str

    RMQ_ROUTING_KEY: str
    RMQ_USER: str
    RMQ_PASS: str
    RMQ_HOST: str
    RMQ_PORT: str

    @property
    def RMQ_URL(self) -> str:
        return (
            f"amqp://{self.RMQ_USER}:{self.RMQ_PASS}@{self.RMQ_HOST}:{self.RMQ_PORT}/"
        )

    class Config:
        env_file = ".env"


config = Config()  # type: ignore
