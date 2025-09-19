import logging
from uuid import UUID

from rmq_service import ProduceService
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from reminder_service.models import Status
from reminder_service.schemas import DeliveryMethod, ReminderResponse
from reminder_service.services import DeliveryMethodService, ReminderService
from reminder_service.use_cases import SendRemindersUseCase

logger = logging.getLogger(__name__)


async def send_reminders(
    send_service: ProduceService, reminder_service: ReminderService
):
    send_uc = SendRemindersUseCase(
        event_service=send_service, reminder_service=reminder_service
    )
    await send_uc.execute()


async def handle_error_reminders(
    session_factory: async_sessionmaker[AsyncSession], data: str, **kwargs
):
    reminder = ReminderResponse.model_validate_json(data)
    service = ReminderService(session_factory)
    res = await service.set_status(reminder.id, Status.FAILED)
    if res is None:
        logger.error("Error set failed status for reminder %s", reminder.id)


async def handle_add_delivery_method(
    session_factory: async_sessionmaker[AsyncSession], data: str, **kwargs
):
    method = DeliveryMethod.model_validate_json(data)
    service = DeliveryMethodService(session_factory)
    await service.create(
        id=method.id,
        delivery_method=method.delivery_method,
        contact_value=method.contact_value,
        user_id=method.user_id,
    )


async def handle_remove_delivery_method(
    session_factory: async_sessionmaker[AsyncSession], data: bytes, **kwargs
):
    method_id = UUID(data.decode())
    service = DeliveryMethodService(session_factory)
    res = await service.delete(id=method_id)
    if not res:
        raise ValueError(f"Unable to delete delivery method with id {method_id}")
