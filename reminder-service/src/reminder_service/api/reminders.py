from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, status
from fastapi_pagination import Page, Params

from reminder_service.dependencies import get_reminders_service
from reminder_service.schemas import (
    ReminderCreate,
    ReminderEdit,
    ReminderResponse,
)
from reminder_service.services import ReminderService
from reminder_service.use_cases import (
    AddReminderUseCase,
    DeleteReminderUseCase,
    EditReminderUseCase,
    GetReminderUseCase,
)

router = APIRouter(prefix="/api/reminders", tags=["reminds"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create(
    reminder_service: Annotated[ReminderService, Depends(get_reminders_service)],
    data: ReminderCreate,
    app_user_id: UUID = Header(),
) -> ReminderResponse:
    uc = AddReminderUseCase(reminder_service=reminder_service)
    res = await uc.execute(user_id=app_user_id, data=data)
    return res


@router.get("/my", response_model=Page[ReminderResponse])
async def get_my(
    request: Request,
    pagination_params: Annotated[Params, Depends()],
    reminder_service: Annotated[ReminderService, Depends(get_reminders_service)],
    app_user_id: UUID = Header(),
) -> Page[ReminderResponse]:
    res = await reminder_service.get_reminders_by_user_id(
        page=pagination_params.page,
        page_size=pagination_params.size,
        user_id=app_user_id,
    )
    return res


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_by_id(
    reminder_service: Annotated[ReminderService, Depends(get_reminders_service)],
    reminder_id: UUID,
    app_user_id: UUID = Header(),
) -> ReminderResponse:
    uc = GetReminderUseCase(reminder_service=reminder_service)
    res = await uc.execute(user_id=app_user_id, reminder_id=reminder_id)
    return res


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(
    reminder_service: Annotated[ReminderService, Depends(get_reminders_service)],
    reminder_id: UUID,
    app_user_id: UUID = Header(),
) -> None:
    uc = DeleteReminderUseCase(reminder_service=reminder_service)
    await uc.execute(user_id=app_user_id, reminder_id=reminder_id)


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def edit_by_id(
    reminder_service: Annotated[ReminderService, Depends(get_reminders_service)],
    data: ReminderEdit,
    reminder_id: UUID,
    app_user_id: UUID = Header(),
) -> ReminderResponse:
    uc = EditReminderUseCase(reminder_service=reminder_service)
    res = await uc.execute(user_id=app_user_id, reminder_id=reminder_id, data=data)
    return res
