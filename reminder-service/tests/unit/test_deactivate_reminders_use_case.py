import json
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

from reminder_service.schemas import DeactivatedReminder
from reminder_service.schemas.delivery_methods import DeliveryMethod
from reminder_service.schemas.reminders import ReminderResponse
from reminder_service.use_cases import DeactivateRemindersUseCase


async def test_with_reminders(
    mock_reminder_service: AsyncMock,
    mock_produce_service: AsyncMock,
    reminder: ReminderResponse,
    delivery_method_tg: DeliveryMethod,
):
    mock_reminder_service.deactivate_reminders_by_method.return_value = [reminder]

    deactivated_reminder = DeactivatedReminder.model_validate(
        reminder, from_attributes=True
    )
    json_data = [deactivated_reminder.model_dump(mode="json")]

    uc = DeactivateRemindersUseCase(
        reminder_service=mock_reminder_service, produce_service=mock_produce_service
    )
    await uc.execute(delivery_method_tg.id)

    mock_reminder_service.deactivate_reminders_by_method.assert_awaited_once()
    mock_produce_service.produce.assert_awaited_once()
    rmq_message = json.loads(
        mock_produce_service.produce.await_args_list[0].args[0].body.decode()
    )
    assert rmq_message["reminders"] == json_data
    assert UUID(rmq_message["user_id"]) == reminder.user_id


async def test_without_reminders(
    mock_reminder_service: AsyncMock, mock_produce_service: AsyncMock
):
    mock_reminder_service.deactivate_reminders_by_method.return_value = []

    uc = DeactivateRemindersUseCase(
        reminder_service=mock_reminder_service, produce_service=mock_produce_service
    )
    await uc.execute(uuid4())

    mock_reminder_service.deactivate_reminders_by_method.assert_awaited_once()
    mock_produce_service.produce.assert_not_awaited()


async def test_with_cyrillic(
    mock_reminder_service: AsyncMock,
    mock_produce_service: AsyncMock,
    reminder: ReminderResponse,
    delivery_method_tg: DeliveryMethod,
):
    reminder.title = "Название"
    reminder.content = "Контент"
    mock_reminder_service.deactivate_reminders_by_method.return_value = [reminder]

    deactivated_reminder = DeactivatedReminder.model_validate(
        reminder, from_attributes=True
    )
    json_data = [deactivated_reminder.model_dump(mode="json")]

    uc = DeactivateRemindersUseCase(
        reminder_service=mock_reminder_service, produce_service=mock_produce_service
    )
    await uc.execute(delivery_method_tg.id)

    mock_reminder_service.deactivate_reminders_by_method.assert_awaited_once()
    mock_produce_service.produce.assert_awaited_once()

    rmq_message = json.loads(
        mock_produce_service.produce.await_args_list[0].args[0].body.decode()
    )
    assert rmq_message["reminders"] == json_data
    assert UUID(rmq_message["user_id"]) == reminder.user_id
