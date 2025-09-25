import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tests.config import config
from user_service.models import Base
from user_service.schemas import (
    DeliveryMethodEnum,
    DeliveryMethodResponse,
    MetaData,
    NotificationResponse,
    User,
    UserResponse,
)
from user_service.services import (
    DeliveryMethodsService,
    NotificationService,
    UserService,
)

# Services


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
def delivery_methods_service(async_session_factory) -> DeliveryMethodsService:
    return DeliveryMethodsService(async_session_factory)


@pytest.fixture
def notification_service(async_session_factory) -> NotificationService:
    return NotificationService(async_session_factory)


@pytest.fixture
def user_service(async_session_factory) -> UserService:
    return UserService(async_session_factory)


# Objects


@pytest.fixture
async def sample_user_db(user_service: UserService, user_data: User) -> UserResponse:
    return await user_service.create(
        user_id=user_data.id,
        name=user_data.name,
        email=user_data.email,
    )


@pytest.fixture
async def sample_method_tg_db(
    sample_user_db: User, delivery_methods_service: DeliveryMethodsService
) -> DeliveryMethodResponse:
    return await delivery_methods_service.create(
        sample_user_db.id,
        DeliveryMethodEnum.TELEGRAM,
        "chat_id",
        meta_data=MetaData(username="username"),
    )


@pytest.fixture
async def sample_method_email_db(
    sample_user_db: User, delivery_methods_service: DeliveryMethodsService
) -> DeliveryMethodResponse:
    return await delivery_methods_service.create(
        sample_user_db.id, DeliveryMethodEnum.EMAIL, "example@example.com"
    )


@pytest.fixture
async def sample_notification_db(
    notification_service, sample_user_db, notification_data
) -> NotificationResponse:
    return await notification_service.create(
        user_id=sample_user_db.id,
        title=notification_data.title,
        content=notification_data.content,
    )
