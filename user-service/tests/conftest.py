from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.schemas import User
from src.services import DeliveryMethodsService, UserService
from src.models import Base

from tests.config import config


@pytest.fixture
def sample_user_data():
    return User(id=uuid4(), email="example@example.com", name="John")


@pytest.fixture
async def sample_user(user_service: UserService, sample_user_data: User):
    return await user_service.add(
        user_id=sample_user_data.id,
        name=sample_user_data.name,
        email=sample_user_data.email,
    )


@pytest.fixture
def user_header(sample_user: User):
    return {"app-user-id": str(sample_user.id)}


@pytest.fixture
async def async_session_factory():
    engine = create_async_engine(
        config.DB_URL,
        echo=True,
        pool_size=10,
        max_overflow=20,
        future=True,
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
def delivery_methods_service(async_session_factory):
    return DeliveryMethodsService(async_session_factory)


@pytest.fixture
def user_service(async_session_factory):
    return UserService(async_session_factory)
