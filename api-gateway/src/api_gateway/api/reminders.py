from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, status

from api_gateway.config import config
from api_gateway.dependencies import get_access_token_data
from api_gateway.schemas import (
    AccessTokenData,
    ReminderCreate,
    ReminderEdit,
    ReminderResponse,
)

from .utils import error_handler

router = APIRouter(prefix="/api/reminders", tags=["reminds"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
@error_handler
async def create(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
    data: ReminderCreate,
):
    async with httpx.AsyncClient(base_url=config.REMINDER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.post(
            "/api/reminders/", json=data.model_dump(mode="json"), headers=headers
        )
        response.raise_for_status()
        return response.json()


@router.get("/my", response_model=list[ReminderResponse])
@error_handler
async def get_my(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
):
    async with httpx.AsyncClient(base_url=config.REMINDER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get("/api/reminders/my", headers=headers)
        response.raise_for_status()
        return response.json()


@router.get("/{reminder_id}", response_model=ReminderResponse)
@error_handler
async def get_by_id(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
    reminder_id: UUID,
):
    async with httpx.AsyncClient(base_url=config.REMINDER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.get(f"/api/reminders/{reminder_id}", headers=headers)
        response.raise_for_status()
        return response.json()


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
@error_handler
async def delete_by_id(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
    reminder_id: UUID,
):
    async with httpx.AsyncClient(base_url=config.REMINDER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.delete(f"/api/reminders/{reminder_id}", headers=headers)
        response.raise_for_status()


@router.patch("/{reminder_id}", response_model=ReminderResponse)
@error_handler
async def edit_by_id(
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data)],
    data: ReminderEdit,
    reminder_id: UUID,
):
    async with httpx.AsyncClient(base_url=config.REMINDER_URL, timeout=10.0) as client:
        headers = {"App-User-Id": str(token_data.user_id)}
        response = await client.patch(
            f"/api/reminders/{reminder_id}",
            json=data.model_dump(mode="json"),
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
