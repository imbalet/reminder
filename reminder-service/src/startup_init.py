from datetime import datetime, timezone
from contextlib import asynccontextmanager
import logging

import aio_pika
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config
from src.database import create_tables
from src.services import SendService

logger = logging.getLogger(__name__)


async def send_reminders(
    session_factory: async_sessionmaker[AsyncSession],
    channel_pool: aio_pika.pool.Pool[aio_pika.channel.Channel],
):
    service = SendService(session_factory, channel_pool)
    tasks = await service.get_upcoming_reminders()
    await service.send_reminders(tasks)
    logger.info(f"Sent {len(tasks)} reminders")


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

    yield

    scheduler.shutdown()
    logger.info("App stopped")
