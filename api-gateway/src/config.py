from pydantic_settings import BaseSettings


class Config(BaseSettings):
    AUTH_URL: str
    REMINDER_URL: str
    JWKS_ENDPOINT: str

    @property
    def JWKS_URL(self):
        return f"{self.AUTH_URL}{self.JWKS_ENDPOINT}"

    class Config:
        env_file = ".env"


config = Config()  # type: ignore
