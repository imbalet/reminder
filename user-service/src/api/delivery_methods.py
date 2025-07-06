from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, status, APIRouter, Depends

from src.services import DeliveryMethodsService
from src.schemas import (
    AccesTokenData,
    DeliveryMethod,
    DeliveryMethodResponse,
    DeliveryMethodEdit,
)
from src.dependencies import (
    get_access_token_data,
    get_delivery_methods_service,
)


router = APIRouter(prefix="/api/delivery", tags=["delivery"])


@router.post(
    "/", response_model=DeliveryMethodResponse, status_code=status.HTTP_201_CREATED
)
async def create_method(
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    delivery_method: DeliveryMethod,
):
    # TODO: add validation telegram chat id
    res = await delivery_service.add(
        access_token_data.user_id,
        delivery_method.delivery_method,
        delivery_method.contact_value,
    )
    return res


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_method(
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
):
    res = await delivery_service.remove(access_token_data.user_id, method_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to delivery method with id {method_id}",
        )


@router.get("/{method_id}", response_model=DeliveryMethodResponse)
async def get_method(
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
):
    res = await delivery_service.get(method_id)
    if not res or res.user_id != access_token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to delivery method with id {method_id}",
        )
    return res


@router.get("/users/{user_id}", response_model=list[DeliveryMethodResponse])
async def get_all_methods(
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    user_id: UUID,
):
    if user_id != access_token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to delivery methods of user with id {user_id}",
        )
    res = await delivery_service.get_all(user_id)
    return res


@router.patch("/{method_id}", response_model=DeliveryMethodResponse)
async def edit_method(
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    delivery_service: Annotated[
        DeliveryMethodsService, Depends(get_delivery_methods_service)
    ],
    method_id: UUID,
    data: DeliveryMethodEdit,
):
    res = await delivery_service.edit(method_id, access_token_data.user_id, data)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to delivery method with id {method_id}",
        )
    return res
