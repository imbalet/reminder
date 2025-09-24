from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page, Params

from api_gateway.config import config
from api_gateway.dependencies import get_access_token_data
from api_gateway.schemas import AccessTokenData, ErrorResponse, NotificationResponse

from .utils import error_handler

router = APIRouter(prefix="/api/notification", tags=["notifications"])


@router.get("/my", response_model=Page[NotificationResponse])
@error_handler
async def get_all_notifications(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
    pagination_params: Annotated[Params, Depends()],
):
    async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get(
            "/api/notification/my",
            headers=headers,
            params=pagination_params.model_dump(mode="json"),
        )
        response.raise_for_status()
        return response.json()


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "No access to notification",
        },
    },
)
@error_handler
async def get_notification(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
    notification_id: UUID,
):
    async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get(
            f"/api/notification/{notification_id}", headers=headers
        )
        response.raise_for_status()
        return response.json()


@router.patch(
    "/{notification_id}",
    response_model=NotificationResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "No access to notification",
        },
    },
)
@error_handler
async def read_notification(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
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


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Notification was deleted",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "No access to notification",
        },
    },
)
@error_handler
async def delete_notification(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
    notification_id: UUID,
):
    async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.delete(
            f"/api/notification/{notification_id}",
            headers=headers,
        )
        response.raise_for_status()
