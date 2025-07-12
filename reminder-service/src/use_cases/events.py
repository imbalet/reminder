import logging
from src.services import EventService, ReminderService

__all__ = ["SendRemindersUseCase"]

logger = logging.getLogger(__name__)


class SendRemindersUseCase:
    def __init__(
        self, event_service: EventService, reminder_service: ReminderService
    ) -> None:
        self.event_service = event_service
        self.reminder_service = reminder_service

    async def execute(self):
        reminders = await self.reminder_service.get_upcoming_reminders()
        await self.event_service.send_reminders(reminders)
        logger.info(f"Sent {len(reminders)} reminders")
