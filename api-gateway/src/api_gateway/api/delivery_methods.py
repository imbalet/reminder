from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, status

from api_gateway.config import config
from api_gateway.dependencies import get_access_token_data
from api_gateway.schemas import (
    AccesTokenData,
    DeliveryMethodAdd,
    DeliveryMethodResponse,
)

from .utils import error_handler

router = APIRouter(prefix="/api/delivery", tags=["delivery"])
BASE_URL = config.USER_URL


@router.post(
    "/", response_model=DeliveryMethodResponse, status_code=status.HTTP_201_CREATED
)
@error_handler
async def create_method(
    token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    data: DeliveryMethodAdd,
):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.post(
            "/api/delivery/", json=data.model_dump(mode="json"), headers=headers
        )
        response.raise_for_status()
        return response.json()


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
@error_handler
async def delete_by_id(
    token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    method_id: UUID,
):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.delete(f"/api/delivery/{method_id}", headers=headers)
        response.raise_for_status()


@router.get("/my", response_model=list[DeliveryMethodResponse])
@error_handler
async def get_all_methods(
    token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get("/api/delivery/my", headers=headers)
        response.raise_for_status()
        return response.json()


@router.get("/{method_id}", response_model=DeliveryMethodResponse)
@error_handler
async def get_method(
    token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    method_id: UUID,
):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get(f"/api/delivery/{method_id}", headers=headers)
        response.raise_for_status()
        return response.json()
