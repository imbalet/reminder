import json
from uuid import uuid4

from user_service.event_handler import (
    add_user_callback,
    deactivated_reminders_callback,
    failed_reminders_callback,
)
from user_service.schemas import DeactivatedReminder, Reminder, User


async def test_add_user_callback(mock_user_service, user_data: User):
    await add_user_callback(mock_user_service, user_data.model_dump_json().encode())
    mock_user_service.create.assert_awaited_once()


async def test_failed_reminders_callback(mock_notification_service, reminder: Reminder):
    await failed_reminders_callback(
        mock_notification_service, reminder.model_dump_json().encode()
    )
    mock_notification_service.create.assert_awaited_once()


async def test_deactivated_reminders_callback_one(
    mock_notification_service, deactivated_reminder: DeactivatedReminder
):

    data = {
        "user_id": str(uuid4()),
        "reminders": [deactivated_reminder.model_dump(mode="json")],
    }
    await deactivated_reminders_callback(
        mock_notification_service, json.dumps(data).encode()
    )
    mock_notification_service.create.assert_awaited_once()


async def test_deactivated_reminders_callback_two(
    mock_notification_service, deactivated_reminder: DeactivatedReminder
):

    data = {
        "user_id": str(uuid4()),
        "reminders": [
            deactivated_reminder.model_dump(mode="json"),
            deactivated_reminder.model_dump(mode="json"),
        ],
    }
    await deactivated_reminders_callback(
        mock_notification_service, json.dumps(data).encode()
    )
    mock_notification_service.create.assert_awaited_once()
