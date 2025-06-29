from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Header, status, HTTPException

from src.services.reminder_service import ReminderService
from src.schemas import ReminderCreate, ReminderResponse, ReminerEdit
from src.dependencies import get_reminders_service

router = APIRouter(prefix="/api/reminders", tags=["reminds"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create(
    service: Annotated[ReminderService, Depends(get_reminders_service)],
    data: ReminderCreate,
    app_user_id: UUID = Header(),
):
    res = await service.create_reminder(
        title=data.title,
        content=data.content,
        remind_date=data.remind_date,
        user_id=app_user_id,
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
