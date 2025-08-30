import logging
from uuid import UUID

import httpx

from reminder_service.config import config
from reminder_service.services.reminder_service import ReminderService
from reminder_service.schemas import (
    ReminderCreate,
    ReminderResponse,
    ReminderEdit,
    DeliveryMethod,
)
from reminder_service.use_cases import ForbiddenException


__all__ = [
    "AddReminderUseCase",
    "GetRemindersByUserIdUseCase",
    "GetReminderUseCase",
    "DeleteReminderUseCase",
    "EditReminderUseCase",
]

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
        async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
            response = await client.get(f"/api/delivery/internal/users/{user_id}")
            response.raise_for_status()
            json_data: list[dict] = response.json()
            methods = [DeliveryMethod.model_validate(item) for item in json_data]

        res = await self.reminder_service.create_reminder(
            title=data.title,
            content=data.content,
            remind_date=data.remind_date,
            user_id=user_id,
            delivery_methods=methods,
        )

        logger.info(
            "Reminder added",
            extra={
                "user_id": str(user_id),
                "operation": "add_reminder",
                "result": "success",
            },
        )

        return res


class GetRemindersByUserIdUseCase:
    def __init__(self, reminder_service: ReminderService):
        self.reminder_service = reminder_service

    async def execute(self, user_id: UUID) -> list[ReminderResponse]:
        """Returns the list of reminders for a user

        Args:
            user_id (UUID): User ID

        Returns:
            list[ReminderResponse]: the list of reminders DTOs
        """
        res = await self.reminder_service.get_reminders_by_user_id(user_id=user_id)
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
        res = await self.reminder_service.get_reminder(reminder_id=reminder_id)
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
        res = await self.reminder_service.delete_reminder(
            reminder_id=reminder_id, user_id=user_id
        )
        if not res:
            logger.info(
                "No acces to reminder",
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
            data (ReminerEdit): DTO containing updated reminder data

        Raises:
            ForbiddenException: The reminder doesn't exist or the user doesn't own the reminder

        Returns:
            ReminderResponse: DTO for the edited reminder
        """
        res = await self.reminder_service.edit_reminder(
            data=data, reminder_id=reminder_id, user_id=user_id
        )
        if not res:
            logger.info(
                "No acces to reminder",
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

        return res
