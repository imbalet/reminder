import asyncio
from contextlib import asynccontextmanager
import logging

import aio_pika
from fastapi import FastAPI
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config
from src.database import create_tables
from src.event_handler import add_user_callback, failed_reminders_callback
from src.services import EventService


logger = logging.getLogger(__name__)


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

    redis = aioredis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        db=0,
        max_connections=20,
    )

    app.state.session_factory = AsyncSessionLocal
    app.state.channel_pool = get_channel_pool()
    app.state.redis = redis

    logger.info("DB started")

    add_user_service = EventService(app.state.channel_pool, config.RMQ_USER_ADD_QUEUE)
    failed_reminders = EventService(app.state.channel_pool, config.RMQ_DLQ_NAME)

    add_users_task = asyncio.create_task(
        add_user_service.consume(
            async_callback=add_user_callback, session_factory=AsyncSessionLocal
        )
    )

    failed_reminders_task = asyncio.create_task(
        failed_reminders.consume(
            async_callback=failed_reminders_callback, session_factory=AsyncSessionLocal
        )
    )

    logger.info("Consume tasks started")
    yield
    add_users_task.cancel()
    try:
        await add_users_task
    except asyncio.CancelledError:
        pass

    failed_reminders_task.cancel()
    try:
        await failed_reminders_task
    except asyncio.CancelledError:
        pass
    logger.info("App stopped")
