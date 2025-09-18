import asyncio
from functools import partial

import aio_pika
from aio_pika import ExchangeType
from rmq_service import ConsumeService, ExchangeConfig, QueueConfig
from sqlalchemy.ext.asyncio import async_sessionmaker

from user_service.config import config
from user_service.event_handler import add_user_callback, failed_reminders_callback


async def setup_consume_registered_user_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    add_user_consume = ConsumeService(
        channel_pool,
        queue_config=QueueConfig(name=config.RMQ_USER_ADD_QUEUE),
    )
    await add_user_consume.setup()

    consume_users_task = asyncio.create_task(
        add_user_consume.consume(partial(add_user_callback, session_factory))
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
            partial(failed_reminders_callback, session_factory)
        )
    )
    return failed_reminders_task


async def setup_tasks(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    consume_users_task = await setup_consume_registered_user_task(
        channel_pool, session_factory
    )
    consume_failed_reminders_task = await setup_consume_failed_reminders_task(
        channel_pool, session_factory
    )

    return consume_users_task, consume_failed_reminders_task
