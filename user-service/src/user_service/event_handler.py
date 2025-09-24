import json
import logging
from uuid import UUID

from user_service.schemas import DeactivatedReminder, Reminder, User
from user_service.services import NotificationService, UserService

logger = logging.getLogger(__name__)


async def add_user_callback(user_service: UserService, data: bytes, **kwargs):
    user = User.model_validate_json(data)
    await user_service.create(user_id=user.id, name=user.name, email=user.email)


async def failed_reminders_callback(
    notification_service: NotificationService, data: bytes, **kwargs
):
    try:
        reminder = Reminder.model_validate_json(data)
        await notification_service.create(
            user_id=reminder.user_id,
            title="Failed to send reminder",
            content=f"Reminder with title '{reminder.title}' failed to send.",
        )
    except Exception as e:
        logger.error(f"Error validating failed reminder. Raw data: {data}", exc_info=e)


async def deactivated_reminders_callback(
    notification_service: NotificationService, data: bytes, **kwargs
):
    dict_data = json.loads(data.decode())

    user_id = UUID(dict_data["user_id"])
    reminders = [DeactivatedReminder.model_validate(i) for i in dict_data["reminders"]]
    await notification_service.create(
        user_id=user_id,
        title=f"{len(reminders)} reminder(s) were deactivated",
        content=f"Your reminders have no delivery methods and were disabled:\
{'\n'.join(f'{i.title} - {i.remind_date}' for i in reminders)}",
    )
