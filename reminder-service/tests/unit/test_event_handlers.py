from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from reminder_service.event_handlers import (
    handle_add_delivery_method,
    handle_error_reminders,
    handle_remove_delivery_method,
)
from reminder_service.schemas import ReminderResponse
from reminder_service.schemas.delivery_methods import DeliveryMethod


async def test_handle_remove_delivery_method_method_exists(
    mock_delivery_methods_service: AsyncMock,
    mock_reminder_service: AsyncMock,
    mock_produce_service: AsyncMock,
    reminder: ReminderResponse,
):
    mock_delivery_methods_service.get.return_value = reminder
    mock_delivery_methods_service.delete.return_value = reminder.id
    mock_reminder_service.deactivate_reminders_by_method.return_value = [reminder]

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


async def test_handle_remove_delivery_method_no_method(
    mock_delivery_methods_service: AsyncMock,
    mock_reminder_service: AsyncMock,
    mock_produce_service: AsyncMock,
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


async def test_handle_add_delivery_method(
    mock_delivery_methods_service: AsyncMock, delivery_method_tg: DeliveryMethod
):
    await handle_add_delivery_method(
        mock_delivery_methods_service,
        data=delivery_method_tg.model_dump_json().encode(),
    )
    mock_delivery_methods_service.create.assert_awaited_once()


async def test_handle_error_reminders(
    mock_reminder_service: AsyncMock,
    reminder: ReminderResponse,
):
    await handle_error_reminders(
        mock_reminder_service,
        data=reminder.model_dump_json().encode(),
    )
    mock_reminder_service.set_status.assert_awaited_once()
