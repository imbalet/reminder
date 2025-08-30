import logging
from uuid import UUID

from user_service.services import NotificationService
from user_service.schemas import NotificationResponse
from user_service.use_cases import ForbiddenException, BadRequestException

__all__ = ["GetNotificationUseCase", "ReadNotificationUseCase"]

logger = logging.getLogger()


class GetNotificationUseCase:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    async def execute(
        self, user_id: UUID, notification_id: UUID
    ) -> NotificationResponse:
        """Returns a notification by ID with user validation

        Args:
            user_id (UUID): User ID
            method_id (UUID): Notification ID.

        Raises:
            ForbiddenException: Notification doesn't exist or user doesn't own the notification.

        Returns:
            DeliveryMethodResponse: DTO with notification data.
        """
        res = await self.notification_service.get(notification_id)
        if not res or res.user_id != user_id:
            raise ForbiddenException(
                f"No access to notification with id {notification_id}"
            )
        return res


class ReadNotificationUseCase:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    async def execute(
        self, user_id: UUID, notification_id: UUID
    ) -> NotificationResponse:
        """Marks a notification as read by ID with user validation

        Args:
            user_id (UUID): User ID
            method_id (UUID): Notification ID.

        Raises:
            ForbiddenException: Notification doesn't exist or user doesn't own the notification.

        Returns:
            DeliveryMethodResponse: DTO with notification data.
        """
        res = await self.notification_service.read(notification_id, user_id)
        if not res:
            raise BadRequestException(
                f"Notification with id {notification_id} is already read"
            )
        return res
