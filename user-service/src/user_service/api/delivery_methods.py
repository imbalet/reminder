from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from rmq_service import ProduceService

from user_service.dependencies import (
    get_add_delivery_method_produce_service,
    get_confirm_code_service,
    get_delivery_methods_service,
    get_remove_delivery_method_produce_service,
)
from user_service.schemas import (
    DeliveryMethodAdd,
    DeliveryMethodResponse,
    ErrorResponse,
)
from user_service.services import ConfirmCodesService, DeliveryMethodsService
from user_service.use_cases import (
    AddDeliveryUseCase,
    DeleteMethodUseCase,
    GetMethodUseCase,
)

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


@router.post(
    "/",
    response_model=DeliveryMethodResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Delivery method created",
            "model": DeliveryMethodResponse,
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Invalid or expired Telegram confirmation code",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Delivery method already exists",
        },
    },
)
async def create_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    confirm_service: Annotated[ConfirmCodesService, Depends(get_confirm_code_service)],
    produce_service: Annotated[
        ProduceService, Depends(get_add_delivery_method_produce_service)
    ],
    delivery_method: DeliveryMethodAdd,
):
    uc = AddDeliveryUseCase(
        delivery_service=delivery_service,
        confirm_service=confirm_service,
        produce_service=produce_service,
    )
    res = await uc.execute(user_id=app_user_id, delivery_method=delivery_method)
    return res


@router.get("/my", response_model=list[DeliveryMethodResponse])
async def get_all_methods(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
):
    res = await delivery_service.get_all(app_user_id)
    return res


@router.get(
    "/{method_id}",
    response_model=DeliveryMethodResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Delivery method created",
            "model": DeliveryMethodResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "No access to delivery method",
        },
    },
)
async def get_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
):
    uc = GetMethodUseCase(delivery_service=delivery_service)
    res = await uc.execute(user_id=app_user_id, method_id=method_id)
    return res


@router.delete(
    "/{method_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "No access to delivery method",
        },
    },
)
async def delete_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    produce_service: Annotated[
        ProduceService, Depends(get_remove_delivery_method_produce_service)
    ],
    method_id: UUID,
):
    uc = DeleteMethodUseCase(
        delivery_service=delivery_service, produce_service=produce_service
    )
    await uc.execute(user_id=app_user_id, method_id=method_id)
