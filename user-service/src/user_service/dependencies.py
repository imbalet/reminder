from typing import Annotated

from fastapi import Depends, Request
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from user_service.services import (
    DeliveryMethodsService,
    ConfirmCodesService,
    NotificationService,
)


def get_async_session_factory(req: Request):
    return req.app.state.session_factory  # type: ignore


def get_redis(req: Request):
    return req.app.state.redis  # type: ignore


def get_delivery_methods_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> DeliveryMethodsService:
    return DeliveryMethodsService(session_factory)


def get_confirm_code_service(redis: Annotated[aioredis.Redis, Depends(get_redis)]):
    return ConfirmCodesService(redis)


def get_notification_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> NotificationService:
    return NotificationService(session_factory)
