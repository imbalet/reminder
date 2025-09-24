from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from aio_pika.pool import Pool
from fastapi_pagination import Page, Params
from rmq_service import ProduceService
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tests.config import config
from user_service.models import Base
from user_service.schemas import (
    DeliveryMethodEnum,
    DeliveryMethodResponse,
    EmailDelivery,
    MetaData,
    NotificationResponse,
    TelegramDelivery,
    User,
)
from user_service.services import (
    ConfirmCodesService,
    DeliveryMethodsService,
    NotificationService,
    UserService,
)


@pytest.fixture
def sample_user_data():
    return User(id=uuid4(), email="example@example.com", name="John")


@pytest.fixture
async def sample_user(user_service: UserService, sample_user_data: User):
    return await user_service.create(
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


@pytest.fixture
def sample_delivery_method_tg_response(sample_user):
    return DeliveryMethodResponse(
        id=uuid4(),
        user_id=sample_user.id,
        delivery_method=DeliveryMethodEnum.TELEGRAM,
        contact_value="contact",
        created_at=datetime(year=2025, month=5, day=10, hour=12, minute=42),
        meta_data=MetaData(username="username"),
    )


@pytest.fixture
def sample_delivery_method_tg_add():
    return TelegramDelivery(
        delivery_method=DeliveryMethodEnum.TELEGRAM,
        confirm_code="telegram",
    )


@pytest.fixture
def sample_delivery_method_email_add():
    return EmailDelivery(
        delivery_method=DeliveryMethodEnum.EMAIL,
        contact_value="example@example.com",
    )


@pytest.fixture
def sample_notification(sample_user_data):
    return NotificationResponse(
        user_id=sample_user_data.id,
        title="title",
        content="content",
        id=uuid4(),
        created_at=datetime.now(UTC),
        is_read=False,
    )


@pytest.fixture
def mock_delivery_service(mocker, sample_delivery_method_tg_response):
    def __get_page_args_delivery_methods(page: int, page_size: int, *args, **kwargs):
        return Page.create(
            [sample_delivery_method_tg_response],
            Params(page=page, size=page_size),
            total=100,
        )

    mock = mocker.create_autospec(DeliveryMethodsService)
    mock.create.return_value = sample_delivery_method_tg_response
    mock.get.return_value = sample_delivery_method_tg_response
    mock.get_all.side_effect = __get_page_args_delivery_methods
    mock.delete.return_value = sample_delivery_method_tg_response
    return mock


@pytest.fixture
def mock_confirm_service(mocker):
    mock = mocker.create_autospec(ConfirmCodesService)
    mock.confirm.return_value = "1", "username"
    return mock


@pytest.fixture
def mock_user_service():
    mock = AsyncMock(spec=UserService)
    return mock


@pytest.fixture
def mock_notification_service(mocker, sample_notification):
    def __get_page_args_notifications(page: int, page_size: int, *args, **kwargs):
        return Page.create(
            [sample_notification], Params(page=page, size=page_size), total=100
        )

    mock = mocker.create_autospec(NotificationService)
    mock.get_all.side_effect = __get_page_args_notifications
    mock.get.return_value = sample_notification
    mock.delete.return_value = sample_notification
    return mock


@pytest.fixture
def mock_channel_pool(mocker):
    mock = mocker.create_autospec(Pool)
    return mock


@pytest.fixture
def mock_produce_service(mocker) -> ProduceService:
    mock = mocker.create_autospec(ProduceService)
    return mock
