import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import logging

import aio_pika
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from reminder_service.config import config
from reminder_service.database import create_tables
from reminder_service.schemas import ReminderResponse
from reminder_service.services import SendService, ReminderService, EventService
from reminder_service.use_cases import SendRemindersUseCase
from reminder_service.models import Status

logger = logging.getLogger(__name__)


async def send_reminders(
    session_factory: async_sessionmaker[AsyncSession],
    channel_pool: aio_pika.pool.Pool[aio_pika.channel.Channel],
):
    send_service = SendService(channel_pool)
    reminder_service = ReminderService(session_factory)
    send_uc = SendRemindersUseCase(
        event_service=send_service, reminder_service=reminder_service
    )
    await send_uc.execute()


async def handle_error_reminders(
    data: str, session_factory: async_sessionmaker[AsyncSession]
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

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_reminders,
        "interval",
        minutes=1,
        args=[app.state.session_factory, app.state.channel_pool],
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()

    event_service = EventService(app.state.channel_pool, config.RMQ_DLQ_NAME)
    handle_error_reminders_task = asyncio.create_task(
        event_service.consume(
            queue_name=config.RMQ_DLQ_NAME,
            async_callback=handle_error_reminders,
            session_factory=AsyncSessionLocal,
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
