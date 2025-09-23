import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from reminder_service.models import Base
from reminder_service.schemas import (
    DeliveryMethod,
    DeliveryMethodEnum,
    ReminderResponse,
)
from reminder_service.services import DeliveryMethodService, ReminderService
from tests.config import config


@pytest.fixture
async def async_session_factory():
    engine = create_async_engine(
        config.DB_URL,
        echo=False,
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

    engine.echo = True

    yield AsyncSessionLocal

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def reminder_service(async_session_factory):
    return ReminderService(async_session_factory)


@pytest.fixture
def delivery_methods_service(async_session_factory):
    return DeliveryMethodService(async_session_factory)


@pytest.fixture
async def sample_db_delivery_method_telegram(
    delivery_methods_service: DeliveryMethodService,
):
    res = await delivery_methods_service.create(
        id=uuid4(),
        delivery_method=DeliveryMethodEnum.TELEGRAM,
        contact_value="123",
        user_id=uuid4(),
    )
    return DeliveryMethod.model_validate(res, from_attributes=True)


@pytest.fixture
async def sample_db_delivery_method_email(
    delivery_methods_service: DeliveryMethodService,
):
    res = await delivery_methods_service.create(
        id=uuid4(),
        delivery_method=DeliveryMethodEnum.EMAIL,
        contact_value="example@example.com",
        user_id=uuid4(),
    )
    return DeliveryMethod.model_validate(res, from_attributes=True)


@pytest.fixture
async def sample_db_reminder(
    reminder_service: ReminderService,
    sample_db_delivery_method_email,
    sample_db_delivery_method_telegram,
):
    res = await reminder_service.create(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=datetime.datetime.now() + datetime.timedelta(days=1),
        delivery_method_ids=[
            sample_db_delivery_method_telegram.id,
            sample_db_delivery_method_email.id,
        ],
    )
    return ReminderResponse.model_validate(res, from_attributes=True)
