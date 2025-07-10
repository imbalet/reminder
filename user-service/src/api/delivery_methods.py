from typing import Annotated
from uuid import UUID

from fastapi import status, APIRouter, Depends, Header

from src.services import DeliveryMethodsService, ConfirmCodesService
from src.schemas import (
    DeliveryMethodAdd,
    DeliveryMethodResponse,
    DeliveryMethodEdit,
)
from src.dependencies import get_delivery_methods_service, get_confirm_code_service
from src.use_cases import (
    AddDeliveryUseCase,
    GetMethodUseCase,
    EditMethodUseCase,
    DeleteMethodUseCase,
)

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


@router.post(
    "/", response_model=DeliveryMethodResponse, status_code=status.HTTP_201_CREATED
)
async def create_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    confirm_service: Annotated[ConfirmCodesService, Depends(get_confirm_code_service)],
    delivery_method: DeliveryMethodAdd,
):
    uc = AddDeliveryUseCase(
        delivery_service=delivery_service, confirm_service=confirm_service
    )
    res = await uc.execute(user_id=app_user_id, delivery_method=delivery_method)
    return res


@router.get("/internal/users/{user_id}", response_model=list[DeliveryMethodResponse])
async def get_all_user_methods(
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    user_id: UUID,
):
    # method for internal communication
    # TODO: Add validation
    res = await delivery_service.get_all(user_id, only_confirmed=True)
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


@router.get("/{method_id}", response_model=DeliveryMethodResponse)
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


@router.patch("/{method_id}", response_model=DeliveryMethodResponse)
async def edit_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
    data: DeliveryMethodEdit,
):
    uc = EditMethodUseCase(delivery_service=delivery_service)
    res = await uc.execute(user_id=app_user_id, method_id=method_id, data=data)
    return res


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
):
    uc = DeleteMethodUseCase(delivery_service=delivery_service)
    await uc.execute(user_id=app_user_id, method_id=method_id)
