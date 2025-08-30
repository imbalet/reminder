from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
import httpx

from api_gateway.config import config
from api_gateway.schemas import NotificationResponse, AccesTokenData
from api_gateway.dependencies import get_access_token_data
from .utils import error_handler

router = APIRouter(prefix="/api/notification", tags=["notifications"])


@router.get("/my", response_model=list[NotificationResponse])
@error_handler
async def get_all_notifications(
    token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
):
    async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get("/api/notification/my", headers=headers)
        response.raise_for_status()
        return response.json()


@router.get("/{notification_id}", response_model=NotificationResponse)
@error_handler
async def get_notification(
    token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    notification_id: UUID,
):
    async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get(
            f"/api/notification/{notification_id}", headers=headers
        )
        response.raise_for_status()
        return response.json()


@router.patch("/{notification_id}", response_model=NotificationResponse)
@error_handler
async def read_notification(
    token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    notification_id: UUID,
):
    async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.patch(
            f"/api/notification/{notification_id}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
