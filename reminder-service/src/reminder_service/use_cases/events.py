import asyncio
import logging

from rmq_service import Message, ProduceService

from reminder_service.schemas import ReminderResponse
from reminder_service.services import ReminderService

logger = logging.getLogger(__name__)


class SendRemindersUseCase:

    def __init__(
        self, event_service: ProduceService, reminder_service: ReminderService
    ) -> None:
        self.produce_service = event_service
        self.reminder_service = reminder_service

    async def _send_message(self, reminder: ReminderResponse, sem: asyncio.Semaphore):
        async with sem:
            await self.produce_service.produce(
                Message.from_json(reminder.model_dump(mode="json"))
            )

    async def execute(self):
        reminders = await self.reminder_service.get_upcoming_reminders()

        sem = asyncio.Semaphore(100)
        tasks = [asyncio.create_task(self._send_message(m, sem)) for m in reminders]
        await asyncio.gather(*tasks)
        logger.info(f"Sent {len(reminders)} reminders")
