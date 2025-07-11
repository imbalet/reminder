from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, status, HTTPException

from src.config import config
from src.dependencies import get_reminders_service
from src.services.reminder_service import ReminderService
from src.schemas import (
    ReminderCreate,
    ReminderResponse,
    ReminderEdit,
    DeliveryMethod,
)
from .utils import error_handler

router = APIRouter(prefix="/api/reminders", tags=["reminds"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
@error_handler
async def create(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    data: ReminderCreate,
    app_user_id: UUID = Header(),
):
    async with httpx.AsyncClient(base_url=config.USER_URL, timeout=10.0) as client:
        response = await client.get(f"/api/delivery/internal/users/{app_user_id}")
        response.raise_for_status()
        json_data: list[dict] = response.json()
        methods = [DeliveryMethod.model_validate(item) for item in json_data]

    res = await service.create_reminder(
        title=data.title,
        content=data.content,
        remind_date=data.remind_date,
        user_id=app_user_id,
        delivery_methods=methods,
    )
    return res


@router.get("/my", response_model=list[ReminderResponse])
async def get_my(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    app_user_id: UUID = Header(),
):
    res = await service.get_reminders_by_user_id(user_id=app_user_id)
    return res


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_by_id(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    reminder_id: UUID,
    app_user_id: UUID = Header(),
):
    res = await service.get_reminder(reminder_id=reminder_id)
    if not res or res.user_id != app_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to reminder with id {reminder_id}",
        )
    return res


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    reminder_id: UUID,
    app_user_id: UUID = Header(),
):
    res = await service.delete_reminder(reminder_id=reminder_id, user_id=app_user_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to reminder with id {reminder_id}",
        )


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def edit_by_id(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    data: ReminderEdit,
    reminder_id: UUID,
    app_user_id: UUID = Header(),
):
    res = await service.edit_reminder(
        data=data, reminder_id=reminder_id, user_id=app_user_id
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to reminder with id {reminder_id}",
        )
    return res
