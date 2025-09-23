from uuid import uuid4

import pytest

from reminder_service.event_handlers import handle_remove_delivery_method


async def test_method_exists(
    mock_delivery_methods_service, mock_reminder_service, mock_produce_service, reminder
):
    mock_delivery_methods_service.get.return_value = reminder
    mock_delivery_methods_service.delete.return_value = reminder.id

    await handle_remove_delivery_method(
        delivery_method_service=mock_delivery_methods_service,
        reminder_service=mock_reminder_service,
        produce_service=mock_produce_service,
        data=str(uuid4()).encode(),
    )
    mock_delivery_methods_service.get.assert_awaited_once()
    mock_delivery_methods_service.delete.assert_awaited_once()
    mock_produce_service.produce.assert_awaited_once()
    mock_reminder_service.deactivate_reminders_by_method.assert_awaited_once()


async def test_no_method(
    mock_delivery_methods_service, mock_reminder_service, mock_produce_service
):
    mock_delivery_methods_service.get.return_value = None

    with pytest.raises(ValueError):
        await handle_remove_delivery_method(
            delivery_method_service=mock_delivery_methods_service,
            reminder_service=mock_reminder_service,
            produce_service=mock_produce_service,
            data=str(uuid4()).encode(),
        )
    mock_delivery_methods_service.get.assert_awaited_once()
    mock_delivery_methods_service.delete.assert_not_awaited()
    mock_produce_service.produce.assert_not_awaited()
    mock_reminder_service.deactivate_reminders_by_method.assert_not_awaited()
