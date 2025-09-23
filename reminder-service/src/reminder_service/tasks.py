import asyncio
import logging
from datetime import datetime, timezone
from functools import partial

import aio_pika
from aio_pika import ExchangeType
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from rmq_service import ConsumeService, ExchangeConfig, ProduceService, QueueConfig
from sqlalchemy.ext.asyncio import async_sessionmaker

from reminder_service.config import config
from reminder_service.event_handlers import (
    handle_add_delivery_method,
    handle_error_reminders,
    handle_remove_delivery_method,
    send_reminders,
)
from reminder_service.services import DeliveryMethodService, ReminderService

logger = logging.getLogger(__name__)


def get_delivery_method_service(session_factory: async_sessionmaker):
    return DeliveryMethodService(session_factory)


def get_reminder_service(session_factory: async_sessionmaker):
    return ReminderService(session_factory)


async def setup_send_reminders_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    send_service = ProduceService(channel_pool, routing_key=config.RMQ_REMINDERS_QUEUE)
    await send_service.setup()
    reminder_service = ReminderService(session_factory)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_reminders,
        "interval",
        minutes=1,
        args=[send_service, reminder_service],
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()

    return scheduler


async def setup_consume_error_reminders_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    consume_service = ConsumeService(
        channel_pool,
        queue_config=QueueConfig(name=config.RMQ_DLQ_FAILED_REMINDERS_NAME),
        exchange_config=ExchangeConfig(
            name=config.RMQ_DLX_FAILED_REMINDERS_NAME, type=ExchangeType.FANOUT
        ),
    )
    await consume_service.setup()
    handle_error_reminders_task = asyncio.create_task(
        consume_service.consume(
            partial(
                handle_error_reminders,
                reminder_service=get_reminder_service(session_factory),
            ),
        )
    )
    return handle_error_reminders_task


async def setup_consume_delivery_method_add_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    consume_service = ConsumeService(
        channel_pool,
        queue_config=QueueConfig(name=config.RMQ_DELIVERY_METHOD_ADD_QUEUE),
    )
    await consume_service.setup()
    handle_error_reminders_task = asyncio.create_task(
        consume_service.consume(
            partial(
                handle_add_delivery_method,
                delivery_method_service=get_delivery_method_service(session_factory),
            ),
        )
    )
    return handle_error_reminders_task


async def setup_consume_delivery_method_remove_task(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    consume_service = ConsumeService(
        channel_pool,
        queue_config=QueueConfig(name=config.RMQ_DELIVERY_METHOD_REMOVE_QUEUE),
    )
    await consume_service.setup()

    produce_service = ProduceService(
        channel_pool=channel_pool, routing_key=config.RMQ_REMINDER_DEACTIVATE_QUEUE
    )
    await produce_service.setup()

    handle_error_reminders_task = asyncio.create_task(
        consume_service.consume(
            partial(
                handle_remove_delivery_method,
                delivery_method_service=get_delivery_method_service(session_factory),
                reminder_service=get_reminder_service(session_factory),
                produce_service=produce_service,
            ),
        )
    )
    return handle_error_reminders_task


async def setup_tasks(
    channel_pool: aio_pika.pool.Pool, session_factory: async_sessionmaker
):
    send_reminder_task_scheduler = await setup_send_reminders_task(
        channel_pool, session_factory
    )
    consume_error_reminders_task = await setup_consume_error_reminders_task(
        channel_pool, session_factory
    )

    consume_delivery_method_add_task = await setup_consume_delivery_method_add_task(
        channel_pool, session_factory
    )
    consume_delivery_method_remove_task = (
        await setup_consume_delivery_method_remove_task(channel_pool, session_factory)
    )
    return (
        send_reminder_task_scheduler,
        consume_error_reminders_task,
        consume_delivery_method_add_task,
        consume_delivery_method_remove_task,
    )
