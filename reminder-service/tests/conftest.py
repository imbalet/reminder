import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from aio_pika import Channel
from aio_pika.pool import Pool
from rmq_service import ProduceService
from sqlalchemy.ext.asyncio import async_sessionmaker

from reminder_service.schemas import (
    DeliveryMethod,
    DeliveryMethodEnum,
    ReminderCreate,
    ReminderResponse,
    Status,
)
from reminder_service.schemas.delivery_methods import MetaData
from reminder_service.services import DeliveryMethodService, ReminderService

# Services


@pytest.fixture
def mock_async_session_factory():
    mock = AsyncMock(spec=async_sessionmaker)
    return mock


@pytest.fixture
def mock_channel_pool():
    mock = AsyncMock(spec=Pool[Channel])
    return mock


@pytest.fixture
def mock_reminder_service():
    return AsyncMock(spec=ReminderService)


@pytest.fixture
def mock_produce_service():
    return AsyncMock(spec=ProduceService)


@pytest.fixture
def mock_delivery_methods_service():
    return AsyncMock(spec=DeliveryMethodService)


# Objects


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def delivery_method_tg(user_id):
    return DeliveryMethod(
        id=uuid4(),
        user_id=user_id,
        delivery_method=DeliveryMethodEnum.TELEGRAM,
        contact_value="contact",
        meta_data=MetaData(username="user"),
    )


@pytest.fixture
def reminder_create(delivery_method_tg):
    return ReminderCreate(
        title="title",
        content="content",
        remind_date=datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
        delivery_methods_ids=[delivery_method_tg.id],
    )


@pytest.fixture
def reminder(user_id, delivery_method_tg):
    return ReminderResponse(
        id=uuid4(),
        title="title",
        content="content",
        remind_date=datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
        user_id=user_id,
        created_at=datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=1),
        status=Status.PENDING,
        edited_at=None,
        delivery_methods=[delivery_method_tg],
    )
