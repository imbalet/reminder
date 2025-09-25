from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from reminder_service.schemas import ReminderEdit
from reminder_service.schemas.reminders import ReminderCreate, ReminderResponse
from reminder_service.use_cases import (
    AddReminderUseCase,
    BadRequestException,
    DeleteReminderUseCase,
    EditReminderUseCase,
    ForbiddenException,
    SendRemindersUseCase,
)


async def test_add_reminder(
    mock_reminder_service: AsyncMock,
    reminder_create: ReminderCreate,
    user_id: UUID,
    reminder: ReminderResponse,
):
    mock_reminder_service.create.return_value = reminder

    uc = AddReminderUseCase(mock_reminder_service)
    res = await uc.execute(user_id, reminder_create)

    assert res.title == reminder_create.title


async def test_add_reminder_exception(
    mock_reminder_service: AsyncMock, reminder_create: ReminderCreate, user_id: UUID
):
    mock_reminder_service.create.side_effect = ValueError()

    uc = AddReminderUseCase(mock_reminder_service)

    with pytest.raises(BadRequestException):
        await uc.execute(user_id, reminder_create)


async def test_delete_reminder(
    mock_reminder_service: AsyncMock,
    user_id: UUID,
    reminder: ReminderResponse,
):
    mock_reminder_service.delete.return_value = reminder

    uc = DeleteReminderUseCase(mock_reminder_service)
    await uc.execute(user_id, reminder.id)


async def test_delete_reminder_exception(
    mock_reminder_service: AsyncMock, reminder: ReminderResponse, user_id: UUID
):
    mock_reminder_service.delete.return_value = None

    uc = DeleteReminderUseCase(mock_reminder_service)

    with pytest.raises(ForbiddenException):
        await uc.execute(user_id, reminder.id)


async def test_edit_reminder(
    mock_reminder_service: AsyncMock, reminder: ReminderResponse, user_id: UUID
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )
    mock_reminder_service.edit.return_value = reminder

    uc = EditReminderUseCase(mock_reminder_service)
    res = await uc.execute(user_id, reminder.id, new_data)

    assert res


async def test_edit_reminder_not_found(
    mock_reminder_service: AsyncMock, reminder: ReminderResponse, user_id: UUID
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )
    mock_reminder_service.edit.return_value = None

    uc = EditReminderUseCase(mock_reminder_service)
    with pytest.raises(ForbiddenException):
        await uc.execute(user_id, reminder.id, new_data)


async def test_edit_reminder_invalid_methods(
    mock_reminder_service: AsyncMock, reminder: ReminderResponse, user_id: UUID
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )
    mock_reminder_service.edit.side_effect = ValueError()

    uc = EditReminderUseCase(mock_reminder_service)
    with pytest.raises(BadRequestException):
        await uc.execute(user_id, reminder.id, new_data)


async def test_send_reminders(
    mock_reminder_service: AsyncMock,
    mock_produce_service: AsyncMock,
    reminder: ReminderResponse,
):
    mock_reminder_service.get_upcoming_reminders.return_value = [reminder]

    uc = SendRemindersUseCase(mock_produce_service, mock_reminder_service)
    await uc.execute()

    mock_reminder_service.get_upcoming_reminders.assert_awaited_once()
    mock_produce_service.produce.assert_awaited()


async def test_send_reminders_empty(
    mock_reminder_service: AsyncMock, mock_produce_service: AsyncMock
):
    mock_reminder_service.get_upcoming_reminders.return_value = []

    uc = SendRemindersUseCase(mock_produce_service, mock_reminder_service)
    await uc.execute()

    mock_reminder_service.get_upcoming_reminders.assert_awaited_once()
    mock_produce_service.produce.assert_not_awaited()
