import logging
from uuid import UUID

from rmq_service import ProduceService

from reminder_service.models import Status
from reminder_service.schemas import DeliveryMethod, ReminderResponse
from reminder_service.services import DeliveryMethodService, ReminderService
from reminder_service.use_cases import DeactivateRemindersUseCase, SendRemindersUseCase

logger = logging.getLogger(__name__)


async def send_reminders(
    send_service: ProduceService, reminder_service: ReminderService
):
    send_uc = SendRemindersUseCase(
        event_service=send_service, reminder_service=reminder_service
    )
    await send_uc.execute()


async def handle_error_reminders(
    reminder_service: ReminderService, data: str, **kwargs
):
    reminder = ReminderResponse.model_validate_json(data)
    res = await reminder_service.set_status(reminder.id, Status.FAILED)
    if res is None:
        logger.error("Error set failed status for reminder %s", reminder.id)


async def handle_add_delivery_method(
    delivery_method_service: DeliveryMethodService, data: str, **kwargs
):
    method = DeliveryMethod.model_validate_json(data)
    await delivery_method_service.create(
        id=method.id,
        delivery_method=method.delivery_method,
        contact_value=method.contact_value,
        user_id=method.user_id,
    )
    logger.info("Delivery method with id %s was added", method.id)


async def handle_remove_delivery_method(
    delivery_method_service: DeliveryMethodService,
    reminder_service: ReminderService,
    produce_service: ProduceService,
    data: bytes,
    **kwargs,
):
    method_id = UUID(data.decode())

    method = await delivery_method_service.get(method_id)
    if not method:
        raise ValueError(f"Method with id {method_id} does not exists")

    uc = DeactivateRemindersUseCase(
        reminder_service=reminder_service, produce_service=produce_service
    )
    await uc.execute(delivery_method_id=method_id)

    res = await delivery_method_service.delete(id=method_id)
    if not res:
        raise ValueError(f"Unable to delete delivery method with id {method_id}")

    logger.info("Delivery method with id %s was removed", method.id)
