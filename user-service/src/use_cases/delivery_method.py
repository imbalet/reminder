import logging
from uuid import UUID

from src.services import DeliveryMethodsService, ConfirmCodesService
from src.schemas import (
    DeliveryMethodAdd,
    DeliveryMethodResponse,
    DeliveryMethodEnum,
)
from src.use_cases import BadRequestException, ForbiddenException

__all__ = [
    "AddDeliveryUseCase",
    "GetMethodUseCase",
    "DeleteMethodUseCase",
]

logger = logging.getLogger()


class AddDeliveryUseCase:
    def __init__(
        self,
        delivery_service: DeliveryMethodsService,
        confirm_service: ConfirmCodesService,
    ):
        self.delivery_service = delivery_service
        self.confirm_service = confirm_service

    async def execute(
        self, user_id: UUID, delivery_method: DeliveryMethodAdd
    ) -> DeliveryMethodResponse:
        """Adds a delivery method for the user

        Args:
            user_id (UUID): User ID
            delivery_method (DeliveryMethod): DTO with delivery method type and value.

        Raises:
            BadRequestException: Raised when invalid or expired confirmation code is provided.

        Returns:
            DeliveryMethodResponse: DTO with added delivery method data.
        """
        if delivery_method.delivery_method == DeliveryMethodEnum.TELEGRAM:
            # Pydantic handles None validation for confirm_code
            chat_id = await self.confirm_service.confirm(delivery_method.confirm_code)  # type: ignore
            if not chat_id:
                logger.info(
                    "Invalid confirmation code",
                    extra={
                        "user_id": str(user_id),
                        "method_type": delivery_method.delivery_method.value,
                        "operation": "add_delivery_method",
                        "result": "error",
                    },
                )
                raise BadRequestException(
                    "Invalid or expired Telegram confirmation code"
                )
            res = await self.delivery_service.add(
                user_id, delivery_method.delivery_method, chat_id, is_confirmed=True
            )
        else:
            # Pydantic handles None validation for confirm_code
            res = await self.delivery_service.add(
                user_id,
                delivery_method.delivery_method,
                delivery_method.contact_value,  # type: ignore
            )

        logger.info(
            "Delivery method added",
            extra={
                "user_id": str(user_id),
                "method_type": delivery_method.delivery_method.value,
                "operation": "add_delivery_method",
                "result": "success",
            },
        )

        return res


class GetMethodUseCase:
    def __init__(self, delivery_service: DeliveryMethodsService):
        self.delivery_service = delivery_service

    async def execute(self, user_id: UUID, method_id: UUID) -> DeliveryMethodResponse:
        """Returns a delivery method by ID with user validation

        Args:
            user_id (UUID): User ID
            method_id (UUID): Delivery method ID.

        Raises:
            ForbiddenException: Delivery method doesn't exist or user doesn't own the method.

        Returns:
            DeliveryMethodResponse: DTO with delivery method data.
        """
        res = await self.delivery_service.get(method_id)
        if not res or res.user_id != user_id:
            raise ForbiddenException(
                f"No access to delivery method with id {method_id}"
            )
        return res


class DeleteMethodUseCase:
    def __init__(self, delivery_service: DeliveryMethodsService):
        self.delivery_service = delivery_service

    async def execute(self, user_id: UUID, method_id: UUID) -> None:
        """Deletes the delivery method with user validation

        Args:
            user_id (UUID): User ID
            method_id (UUID): Method ID

        Raises:
            ForbiddenException: Delivery method doesn't exist or user doesn't own the method.
        """
        res = await self.delivery_service.delete(user_id, method_id)
        if not res:
            logger.info(
                "No acces to method",
                extra={
                    "user_id": str(user_id),
                    "method_type": None,
                    "operation": "delete_delivery_method",
                    "result": "error",
                },
            )
            raise ForbiddenException(
                f"No access to delivery method with id {method_id}",
            )

        logger.info(
            "Delivery method deleted",
            extra={
                "user_id": str(user_id),
                "method_type": res.delivery_method.value,
                "operation": "delete_delivery_method",
                "result": "success",
            },
        )
