import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import partial

import aio_pika
from aio_pika import ExchangeType
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from rmq_service import ConsumeService, ExchangeConfig, ProduceService, QueueConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from reminder_service.config import config
from reminder_service.database import create_tables
from reminder_service.models import Status
from reminder_service.schemas import ReminderResponse
from reminder_service.services import ReminderService
from reminder_service.use_cases import SendRemindersUseCase

logger = logging.getLogger(__name__)


async def send_reminders(
    send_service: ProduceService, reminder_service: ReminderService
):
    send_uc = SendRemindersUseCase(
        event_service=send_service, reminder_service=reminder_service
    )
    await send_uc.execute()


async def handle_error_reminders(
    session_factory: async_sessionmaker[AsyncSession], data: str
):
    reminder = ReminderResponse.model_validate_json(data)
    service = ReminderService(session_factory)
    res = await service.set_status(reminder.id, Status.FAILED)
    if res is None:
        logger.error("")


def get_channel_pool():
    async def create_connection():
        return await aio_pika.connect_robust(config.RMQ_URL)

    async def create_channel():
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    connection_pool = aio_pika.pool.Pool(create_connection, max_size=10)
    channel_pool = aio_pika.pool.Pool(create_channel, max_size=100)
    return channel_pool


@asynccontextmanager
async def startup_event(app: FastAPI):
    engine = create_async_engine(
        config.DB_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        future=True,
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    await create_tables(engine)
    app.state.session_factory = AsyncSessionLocal
    app.state.channel_pool = get_channel_pool()

    logger.info("DB started")

    send_service = ProduceService(
        app.state.channel_pool, routing_key=config.RMQ_REMINDERS_QUEUE
    )
    await send_service.setup()
    reminder_service = ReminderService(app.state.session_factory)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_reminders,
        "interval",
        minutes=1,
        args=[send_service, reminder_service],
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()

    consume_service = ConsumeService(
        app.state.channel_pool,
        queue_config=QueueConfig(name=config.RMQ_DLQ_FAILED_REMINDERS_NAME),
        exchange_config=ExchangeConfig(
            name=config.RMQ_DLX_FAILED_REMINDERS_NAME, type=ExchangeType.FANOUT
        ),
    )
    await consume_service.setup()
    handle_error_reminders_task = asyncio.create_task(
        consume_service.consume(
            partial(handle_error_reminders, app.state.session_factory),
        )
    )

    yield
    handle_error_reminders_task.cancel()
    try:
        await handle_error_reminders_task
    except asyncio.CancelledError:
        pass

    scheduler.shutdown()
    logger.info("App stopped")
