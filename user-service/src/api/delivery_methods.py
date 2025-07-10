from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, status, APIRouter, Depends, Header

from src.services import DeliveryMethodsService, ConfirmCodesService
from src.schemas import (
    DeliveryMethod,
    DeliveryMethodResponse,
    DeliveryMethodEdit,
    DeliveryMethodEnum,
)
from src.dependencies import get_delivery_methods_service, get_confirm_code_service


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
    delivery_method: DeliveryMethod,
):
    if delivery_method.delivery_method == DeliveryMethodEnum.TELEGRAM:
        chat_id = await confirm_service.confirm(delivery_method.contact_value)
        if not chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired Telegram confirmation code",
            )
        res = await delivery_service.add(
            app_user_id, delivery_method.delivery_method, chat_id, is_confirmed=True
        )

    else:
        res = await delivery_service.add(
            app_user_id,
            delivery_method.delivery_method,
            delivery_method.contact_value,
        )

    return res


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
):
    res = await delivery_service.remove(app_user_id, method_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to delivery method with id {method_id}",
        )


@router.get("/my", response_model=list[DeliveryMethodResponse])
async def get_all_methods(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
):
    res = await delivery_service.get_all(app_user_id)
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


@router.get("/{method_id}", response_model=DeliveryMethodResponse)
async def get_method(
    app_user_id: Annotated[UUID, Header()],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
):
    res = await delivery_service.get(method_id)
    if not res or res.user_id != app_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to delivery method with id {method_id}",
        )
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
    res = await delivery_service.edit(method_id, app_user_id, data)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to delivery method with id {method_id}",
        )
    return res
