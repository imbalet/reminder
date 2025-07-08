import functools

from typing import Annotated, Callable, Any
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, status, HTTPException

from src.services.reminder_service import ReminderService
from src.schemas import (
    ReminderCreate,
    ReminderResponse,
    ReminerEdit,
    DeliveryMethod,
)
from src.dependencies import get_reminders_service
from src.config import config

router = APIRouter(prefix="/api/reminders", tags=["reminds"])


def error_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                original_detail = error_data.get("detail", error_data)
                detail_value = original_detail
            except Exception:
                detail_value = e.response.text
            raise HTTPException(
                status_code=e.response.status_code,
                detail=detail_value,
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, detail=f"Service unavailable: {str(e)}"
            )

    return wrapper


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
    res = await service.get_reminders_by_user_id(app_user_id)
    return res


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_by_id(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    reminder_id: UUID,
    app_user_id: UUID = Header(),
):
    res = await service.get_reminder(reminder_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if res.user_id != app_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return res


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    reminder_id: UUID,
    app_user_id: UUID = Header(),
):
    reminder = await service.get_reminder(reminder_id)
    if reminder is None or reminder.user_id != app_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await service.delete_reminder(reminder_id)


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def edit_by_id(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    data: ReminerEdit,
    reminder_id: UUID,
    app_user_id: UUID = Header(),
):
    reminder = await service.get_reminder(reminder_id)
    if reminder is None or reminder.user_id != app_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    res = await service.edit_reminder(data=data, reminder_id=reminder_id)
    return res
