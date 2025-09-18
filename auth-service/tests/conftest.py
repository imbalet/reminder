import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from auth_service.models import Base
from auth_service.services import RefreshTokenService, UserService
from config import config


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
    return UserService(async_session_factory)


@pytest.fixture
def token_service(async_session_factory):
    return RefreshTokenService(async_session_factory)
