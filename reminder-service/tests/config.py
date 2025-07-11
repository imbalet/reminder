from pydantic_settings import BaseSettings


class Config(BaseSettings):
    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_NAME: str
    TEST_DB_USER: str
    TEST_DB_PASS: str

    TEST_RMQ_ROUTING_KEY: str
    TEST_RMQ_USER: str
    TEST_RMQ_PASS: str
    TEST_RMQ_HOST: str
    TEST_RMQ_PORT: str

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@"
            f"{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )

    @property
    def RMQ_URL(self) -> str:
        return f"amqp://{self.TEST_RMQ_USER}:{self.TEST_RMQ_PASS}@{self.TEST_RMQ_HOST}:{self.TEST_RMQ_PORT}/"

    class Config:
        env_file = "tests/.env.test"


config = Config()  # type: ignore
