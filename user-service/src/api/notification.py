from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from src.services import NotificationService
from src.schemas import NotificationResponse, ErrorResponse
from src.dependencies import get_notification_service
from src.use_cases import GetNotificationUseCase, ReadNotificationUseCase


router = APIRouter(prefix="/api/notification", tags=["notifications"])


@router.get("/my", response_model=list[NotificationResponse])
async def get_all_notifications(
    app_user_id: Annotated[UUID, Header()],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
):
    res = await notification_service.get_all(app_user_id)
    return res


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
async def get_notification(
    app_user_id: Annotated[UUID, Header()],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
    notification_id: UUID,
):
    uc = GetNotificationUseCase(notification_service=notification_service)
    res = await uc.execute(user_id=app_user_id, notification_id=notification_id)
    return res


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
async def read_notification(
    app_user_id: Annotated[UUID, Header()],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
    notification_id: UUID,
):
    uc = ReadNotificationUseCase(notification_service=notification_service)
    res = await uc.execute(user_id=app_user_id, notification_id=notification_id)
    return res
