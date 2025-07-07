from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, status, APIRouter, Depends, Header

from src.services import DeliveryMethodsService
from src.schemas import (
    DeliveryMethod,
    DeliveryMethodResponse,
    DeliveryMethodEdit,
)
from src.dependencies import (
    get_delivery_methods_service,
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
    delivery_method: DeliveryMethod,
):
    # TODO: add validation telegram chat id
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
