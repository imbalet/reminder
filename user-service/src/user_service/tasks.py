import asyncio
from functools import partial

import aio_pika
from aio_pika import ExchangeType
from rmq_service import ConsumeService, ExchangeConfig, QueueConfig
from sqlalchemy.ext.asyncio import async_sessionmaker

from user_service.config import config
from user_service.event_handler import (
    add_user_callback,
    deactivated_reminders_callback,
    failed_reminders_callback,
)
from user_service.services import (
    NotificationService,
    UserService,
)


def get_notification_service(session_factory: async_sessionmaker):
    return NotificationService(session_factory=session_factory)


def get_user_service(session_factory: async_sessionmaker):
    return UserService(session_factory=session_factory)


async def setup_consume_registered_user_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    add_user_consume = ConsumeService(
        channel_pool,
        queue_config=QueueConfig(name=config.RMQ_USER_ADD_QUEUE),
    )
    await add_user_consume.setup()

    consume_users_task = asyncio.create_task(
        add_user_consume.consume(
            partial(add_user_callback, user_service=get_user_service(session_factory))
        )
    )
    return consume_users_task


async def setup_consume_failed_reminders_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    failed_reminders_consume = ConsumeService(
        channel_pool,
        queue_config=QueueConfig(name=config.RMQ_DLQ_FAILED_REMINDERS_NAME),
        exchange_config=ExchangeConfig(
            name=config.RMQ_DLX_FAILED_REMINDERS_NAME, type=ExchangeType.FANOUT
        ),
    )
    await failed_reminders_consume.setup()

    failed_reminders_task = asyncio.create_task(
        failed_reminders_consume.consume(
            partial(
                failed_reminders_callback,
                notification_service=get_notification_service(session_factory),
            )
        )
    )
    return failed_reminders_task


async def setup_consume_deactivated_reminders_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    deactivated_reminders_consume = ConsumeService(
        channel_pool,
        queue_config=QueueConfig(name=config.RMQ_REMINDER_DEACTIVATE_QUEUE),
    )
    await deactivated_reminders_consume.setup()

    deactivated_reminders_task = asyncio.create_task(
        deactivated_reminders_consume.consume(
            partial(
                deactivated_reminders_callback,
                notification_service=get_notification_service(session_factory),
            )
        )
    )
    return deactivated_reminders_task


async def setup_tasks(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    consume_users_task = await setup_consume_registered_user_task(
        channel_pool, session_factory
    )
    consume_failed_reminders_task = await setup_consume_failed_reminders_task(
        channel_pool, session_factory
    )
    consume_deactivated_reminders_task = await setup_consume_deactivated_reminders_task(
        channel_pool, session_factory
    )

    return {
        "tasks": [
            consume_users_task,
            consume_failed_reminders_task,
            consume_deactivated_reminders_task,
        ]
    }
