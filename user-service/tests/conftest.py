from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from aio_pika.pool import Pool
from fastapi_pagination import Page, Params
from pytest_mock import MockerFixture
from redis.asyncio import Redis
from rmq_service import ProduceService
from sqlalchemy.ext.asyncio import async_sessionmaker

from user_service.schemas import (
    DeactivatedReminder,
    DeliveryMethodEnum,
    DeliveryMethodResponse,
    EmailDelivery,
    MetaData,
    NotificationResponse,
    Reminder,
    TelegramDelivery,
    User,
)
from user_service.schemas.reminder import DeliveryMethod as ReminderDeliveryMethod
from user_service.services import (
    ConfirmCodesService,
    DeliveryMethodsService,
    NotificationService,
    UserService,
)

# Objects


@pytest.fixture
def user_data() -> User:
    return User(id=uuid4(), email="example@example.com", name="John")


@pytest.fixture
def delivery_method_tg_response(user_data) -> DeliveryMethodResponse:
    return DeliveryMethodResponse(
        id=uuid4(),
        user_id=user_data.id,
        delivery_method=DeliveryMethodEnum.TELEGRAM,
        contact_value="contact",
        created_at=datetime(year=2025, month=5, day=10, hour=12, minute=42),
        meta_data=MetaData(username="username"),
    )


@pytest.fixture
def delivery_method_tg_add() -> TelegramDelivery:
    return TelegramDelivery(
        delivery_method=DeliveryMethodEnum.TELEGRAM,
        confirm_code="telegram",
    )


@pytest.fixture
def delivery_method_email_add() -> EmailDelivery:
    return EmailDelivery(
        delivery_method=DeliveryMethodEnum.EMAIL,
        contact_value="example@example.com",
    )


@pytest.fixture
def notification_data(user_data) -> NotificationResponse:
    return NotificationResponse(
        user_id=user_data.id,
        title="title",
        content="content",
        id=uuid4(),
        created_at=datetime.now(UTC),
        is_read=False,
    )


@pytest.fixture
def reminder(user_data, delivery_method_tg_response) -> Reminder:
    return Reminder(
        id=uuid4(),
        user_id=user_data.id,
        title="title",
        content="content",
        remind_date=datetime.now(UTC) + timedelta(hours=1),
        created_at=datetime.now(UTC) - timedelta(hours=1),
        edited_at=None,
        delivery_methods=[
            ReminderDeliveryMethod(
                id=delivery_method_tg_response.id,
                delivery_method=delivery_method_tg_response.delivery_method,
                contact_value=delivery_method_tg_response.contact_value,
            )
        ],
    )


@pytest.fixture
def deactivated_reminder() -> DeactivatedReminder:
    return DeactivatedReminder(
        id=uuid4(),
        title="title",
        content="content",
        remind_date=datetime.now(UTC) + timedelta(hours=1),
    )


# Services


@pytest.fixture
def mock_async_session_factory():
    return AsyncMock(spec=async_sessionmaker)


@pytest.fixture
def mock_channel_pool(mocker):
    mock = mocker.create_autospec(Pool)
    return mock


@pytest.fixture
def mock_redis():
    return AsyncMock(spec=Redis)


@pytest.fixture
def mock_delivery_service(mocker, delivery_method_tg_response):
    def __get_page_args_delivery_methods(page: int, page_size: int, *args, **kwargs):
        return Page.create(
            [delivery_method_tg_response],
            Params(page=page, size=page_size),
            total=100,
        )

    mock = mocker.create_autospec(DeliveryMethodsService)
    mock.create.return_value = delivery_method_tg_response
    mock.get.return_value = delivery_method_tg_response
    mock.get_all.side_effect = __get_page_args_delivery_methods
    mock.delete.return_value = delivery_method_tg_response
    return mock


@pytest.fixture
def mock_confirm_service_with_redis(mock_redis) -> ConfirmCodesService:
    return ConfirmCodesService(mock_redis)


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
def mock_notification_service(mocker: MockerFixture, notification_data):
    def __get_page_args_notifications(page: int, page_size: int, *args, **kwargs):
        return Page.create(
            [notification_data], Params(page=page, size=page_size), total=100
        )

    mock = mocker.create_autospec(NotificationService)
    mock.get_all.side_effect = __get_page_args_notifications
    mock.get.return_value = notification_data
    mock.delete.return_value = notification_data
    return mock


@pytest.fixture
def mock_produce_service(mocker) -> ProduceService:
    mock = mocker.create_autospec(ProduceService)
    return mock
