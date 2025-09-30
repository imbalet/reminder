from unittest.mock import patch

import pytest
from config import config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth_service.config import Config, LogLevels
from auth_service.models import Base


@pytest.fixture(autouse=True, scope="session")
def patch_config_module():
    fake_config = Config.model_construct(
        LOG_LEVEL=LogLevels("DEBUG"),
        DB_HOST="localhost",
        DB_PORT=5432,
        DB_NAME="test",
        DB_USER="user",
        DB_PASS="pass",
        RMQ_USER_ADD_QUEUE="q1",
        RMQ_USER="guest",
        RMQ_PASS="guest",
        RMQ_HOST="localhost",
        RMQ_PORT=5672,
        ALGORITHM="RS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
        REFRESH_TOKEN_EXPIRE_DAYS=7,
        KEY_PAIR_EXPIRES_DAYS=15,
        ROTATING_BEFORE_EXPIRING_DAYS=2,
    )
    with patch("auth_service.config.Config", return_value=fake_config), patch(
        "auth_service.config.config", fake_config
    ):
        yield


@pytest.fixture
async def async_session_factory():
    engine = create_async_engine(
        config.DB_URL, echo=True, pool_size=10, max_overflow=20, future=True
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield AsyncSessionLocal

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def user_service(async_session_factory):
    from auth_service.services import UserService

    return UserService(async_session_factory)


@pytest.fixture
def token_service(async_session_factory):
    from auth_service.services import RefreshTokenService

    return RefreshTokenService(async_session_factory)
