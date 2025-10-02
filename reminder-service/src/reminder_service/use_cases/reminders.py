import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from rmq_service import Message, ProduceService

from reminder_service.schemas import (
    DeactivatedReminder,
    ReminderCreate,
    ReminderEdit,
    ReminderResponse,
    Status,
)
from reminder_service.services.reminder_service import ReminderService
from reminder_service.use_cases import BadRequestException, ForbiddenException

logger = logging.getLogger()


class AddReminderUseCase:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    async def execute(self, user_id: UUID, data: ReminderCreate) -> ReminderResponse:
        """Adds a reminder for the user

        Args:
            user_id (UUID): User ID
            data (ReminderCreate): DTO containing reminder data

        Returns:
            ReminderResponse: DTO for the created reminder
        """
        try:
            res = await self.reminder_service.create(
                title=data.title,
                content=data.content,
                remind_date=data.remind_date,
                user_id=user_id,
                delivery_method_ids=data.delivery_methods_ids,
            )

            logger.info(
                "Reminder added",
                extra={
                    "user_id": str(user_id),
                    "operation": "add_reminder",
                    "result": "success",
                },
            )
        except ValueError:
            raise BadRequestException("one or more delivery method ids are invalid")

        return res


class GetReminderUseCase:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    async def execute(self, user_id: UUID, reminder_id: UUID) -> ReminderResponse:
        """Returns a reminder by id

        Args:
            user_id (UUID): User ID (reminder owner)
            reminder_id (UUID): Reminder ID

        Raises:
            ForbiddenException: The reminder doesn't exist or the user doesn't own the reminder

        Returns:
            ReminderResponse: DTO for the reminder
        """
        res = await self.reminder_service.get(reminder_id=reminder_id)
        if not res or res.user_id != user_id:
            raise ForbiddenException(f"No access to reminder with id {reminder_id}")
        return res


class DeleteReminderUseCase:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    async def execute(self, user_id: UUID, reminder_id: UUID) -> None:
        """Deletes a reminder

        Args:
            user_id (UUID): User ID (reminder owner)
            reminder_id (UUID): Reminder ID

        Raises:
            ForbiddenException: The reminder doesn't exist or the user doesn't own the reminder
        """
        res = await self.reminder_service.delete(
            reminder_id=reminder_id, user_id=user_id
        )
        if not res:
            logger.info(
                "No access to reminder",
                extra={
                    "user_id": str(user_id),
                    "operation": "delete_reminder",
                    "result": "error",
                },
            )
            raise ForbiddenException(f"No access to reminder with id {reminder_id}")

        logger.info(
            "Reminder deleted",
            extra={
                "user_id": str(user_id),
                "operation": "delete_reminder",
                "result": "success",
            },
        )


class EditReminderUseCase:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    async def execute(
        self, user_id: UUID, reminder_id: UUID, data: ReminderEdit
    ) -> ReminderResponse:
        """Edits a reminder

        Args:
            user_id (UUID): User ID (reminder owner)
            reminder_id (UUID): Reminder ID
            data (ReminderEdit): DTO containing updated reminder data

        Raises:
            ForbiddenException: The reminder doesn't exist or the user doesn't own the reminder
            BadRequestException: One or more delivery methods are forbidden

        Returns:
            ReminderResponse: DTO for the edited reminder
        """

        try:
            res = await self.reminder_service.edit(
                data=data, reminder_id=reminder_id, user_id=user_id
            )
            if not res:
                logger.info(
                    "No access to reminder",
                    extra={
                        "user_id": str(user_id),
                        "operation": "edit_reminder",
                        "result": "error",
                    },
                )
                raise ForbiddenException(f"No access to reminder with id {reminder_id}")
            logger.info(
                "Reminder edited",
                extra={
                    "user_id": str(user_id),
                    "operation": "edit_reminder",
                    "result": "success",
                },
            )
            if res.status == Status.INACTIVE and len(res.delivery_methods) >= 1:
                if res.remind_date >= datetime.now(UTC):
                    await self.reminder_service.set_status(res.id, Status.PENDING)
                else:
                    await self.reminder_service.set_status(res.id, Status.FAILED)
        except ValueError:
            raise BadRequestException("Invalid delivery method(s)")

        return res


class SendRemindersUseCase:

    def __init__(
        self, produce_service: ProduceService, reminder_service: ReminderService
    ) -> None:
        self.produce_service = produce_service
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


class DeactivateRemindersUseCase:

    def __init__(
        self, reminder_service: ReminderService, produce_service: ProduceService
    ):
        self.reminder_service = reminder_service
        self.produce_service = produce_service

    async def execute(self, delivery_method_id: UUID):
        res = await self.reminder_service.deactivate_reminders_by_method(
            delivery_method_id=delivery_method_id
        )
        if len(res) == 0:
            return

        await self.produce_service.produce(
            Message.from_json(
                {
                    "user_id": str(res[0].user_id),
                    "reminders": [
                        DeactivatedReminder.model_validate(
                            i, from_attributes=True
                        ).model_dump(mode="json")
                        for i in res
                    ],
                }
            )
        )
