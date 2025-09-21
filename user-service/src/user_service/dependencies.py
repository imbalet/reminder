from typing import Annotated

from aio_pika.pool import Pool
from fastapi import Depends, Request
from redis import asyncio as aioredis
from rmq_service import ProduceService
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from user_service.config import config
from user_service.services import (
    ConfirmCodesService,
    DeliveryMethodsService,
    NotificationService,
)


def get_async_session_factory(req: Request):
    return req.app.state.session_factory


def get_redis(req: Request):
    return req.app.state.redis


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


def get_channel_pool(req: Request) -> Pool:
    return req.app.state.channel_pool


def get_add_delivery_method_produce_service(
    channel_pool: Annotated[Pool, Depends(get_channel_pool)],
):
    return ProduceService(
        channel_pool=channel_pool, routing_key=config.RMQ_DELIVERY_METHOD_ADD_QUEUE
    )


def get_remove_delivery_method_produce_service(
    channel_pool: Annotated[Pool, Depends(get_channel_pool)],
):
    return ProduceService(
        channel_pool=channel_pool, routing_key=config.RMQ_DELIVERY_METHOD_REMOVE_QUEUE
    )
