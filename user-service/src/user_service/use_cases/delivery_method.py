import logging
from uuid import UUID

from rmq_service import Message, ProduceService

from user_service.schemas import (
    DeliveryMethodAdd,
    DeliveryMethodEnum,
    DeliveryMethodResponse,
    DeliveryMethodRMQ,
    MetaData,
)
from user_service.services import ConfirmCodesService, DeliveryMethodsService
from user_service.use_cases import BadRequestException, ForbiddenException

logger = logging.getLogger()


class AddDeliveryUseCase:

    def __init__(
        self,
        delivery_service: DeliveryMethodsService,
        confirm_service: ConfirmCodesService,
        produce_service: ProduceService,
    ):
        self.delivery_service = delivery_service
        self.confirm_service = confirm_service
        self.produce_service = produce_service

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
            value = await self.confirm_service.confirm(delivery_method.confirm_code)  # type: ignore
            if not value:
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
            chat_id, username = value
            contact_value = chat_id
            meta_data = MetaData(username=username)
        else:
            contact_value = delivery_method.contact_value
            meta_data = None

        res = await self.delivery_service.create(
            user_id,
            delivery_method.delivery_method,
            contact_value,
            is_confirmed=True,
            meta_data=meta_data,
        )
        await self.produce_service.produce(
            Message.from_json(
                DeliveryMethodRMQ.model_validate(res, from_attributes=True).model_dump(
                    mode="json"
                )
            )
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

    def __init__(
        self,
        delivery_service: DeliveryMethodsService,
        produce_service: ProduceService,
    ):
        self.delivery_service = delivery_service
        self.produce_service = produce_service

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
                "No access to method",
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
        await self.produce_service.produce(Message.from_text(str(res.id)))

        logger.info(
            "Delivery method deleted",
            extra={
                "user_id": str(user_id),
                "method_type": res.delivery_method.value,
                "operation": "delete_delivery_method",
                "result": "success",
            },
        )
