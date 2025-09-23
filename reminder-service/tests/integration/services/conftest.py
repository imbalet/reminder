import datetime
from uuid import uuid4

import pytest

from reminder_service.schemas import (
    DeliveryMethod,
    DeliveryMethodEnum,
    ReminderResponse,
)
from reminder_service.services import DeliveryMethodService, ReminderService


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
