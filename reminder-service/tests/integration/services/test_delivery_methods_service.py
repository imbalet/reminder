from uuid import uuid4

from reminder_service.schemas.delivery_methods import DeliveryMethod
from reminder_service.schemas.reminders import ReminderResponse
from reminder_service.services.delivery_method import DeliveryMethodService


async def test_create(
    delivery_methods_service: DeliveryMethodService, delivery_method_tg: DeliveryMethod
):
    res = await delivery_methods_service.create(
        id=delivery_method_tg.id,
        delivery_method=delivery_method_tg.delivery_method,
        contact_value=delivery_method_tg.contact_value,
        user_id=delivery_method_tg.user_id,
    )

    from_db = await delivery_methods_service.get(res.id)
    assert res == delivery_method_tg
    assert res == from_db


async def test_get(
    delivery_methods_service: DeliveryMethodService,
    sample_db_delivery_method_telegram: DeliveryMethod,
):
    res = await delivery_methods_service.get(sample_db_delivery_method_telegram.id)
    assert res == sample_db_delivery_method_telegram


async def test_get_not_exists(delivery_methods_service: DeliveryMethodService):
    res = await delivery_methods_service.get(uuid4())
    assert res is None


async def test_get_by_reminder_id(
    delivery_methods_service: DeliveryMethodService,
    sample_db_reminder: ReminderResponse,
    sample_db_delivery_method_telegram: DeliveryMethod,
    sample_db_delivery_method_email: DeliveryMethod,
):
    res = await delivery_methods_service.get_by_reminder_id(sample_db_reminder.id)

    assert len(res) == 2
    assert sample_db_delivery_method_email in res
    assert sample_db_delivery_method_telegram in res


async def test_get_by_reminder_id_empty(
    delivery_methods_service: DeliveryMethodService,
):
    res = await delivery_methods_service.get_by_reminder_id(uuid4())
    assert len(res) == 0


async def test_delete(
    delivery_methods_service: DeliveryMethodService,
    sample_db_delivery_method_telegram: DeliveryMethod,
):
    res = await delivery_methods_service.delete(sample_db_delivery_method_telegram.id)

    from_db = await delivery_methods_service.get(sample_db_delivery_method_telegram.id)

    assert res == sample_db_delivery_method_telegram.id
    assert from_db is None


async def test_delete_not_exists(delivery_methods_service: DeliveryMethodService):
    method_id = uuid4()

    res = await delivery_methods_service.delete(method_id)

    assert res is None
