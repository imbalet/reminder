import logging

from user_service.schemas import User, Reminder
from user_service.services import UserService, NotificationService

logger = logging.getLogger(__name__)


async def add_user_callback(data: str, session_factory):
    user = User.model_validate_json(data)
    service = UserService(session_factory)
    await service.add(user_id=user.id, name=user.name, email=user.email)


async def failed_reminders_callback(data: str, session_factory):
    try:
        reminder = Reminder.model_validate_json(data)
        service = NotificationService(session_factory)
        await service.create(
            user_id=reminder.user_id,
            title="Failed to send reminder",
            content=f"Reminder with title '{reminder.title}' failed to send.",
        )
    except Exception as e:
        logger.error(f"Error validating failed reminder. Raw data: {data}", exc_info=e)
