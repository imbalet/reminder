import asyncio
from contextlib import asynccontextmanager
from functools import partial

import aio_pika
from fastapi import FastAPI
from redis import asyncio as aioredis
from rmq_service import ConsumeService, ExchangeConfig, QueueConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from user_service.config import config
from user_service.database import create_tables
from user_service.event_handler import add_user_callback, failed_reminders_callback

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

    add_user_consume = ConsumeService(
        app.state.channel_pool,
        queue_config=QueueConfig(name=config.RMQ_USER_ADD_QUEUE),
    )
    await add_user_consume.setup()

    failed_reminders_consume = ConsumeService(
        app.state.channel_pool,
        queue_config=QueueConfig(name=config.RMQ_DLQ_FAILED_REMINDERS_NAME),
        exchange_config=ExchangeConfig(
            name=config.RMQ_DLX_FAILED_REMINDERS_NAME, type=ExchangeType.FANOUT
        ),
    )
    await failed_reminders_consume.setup()

    add_users_task = asyncio.create_task(
        add_user_consume.consume(partial(add_user_callback, AsyncSessionLocal))
    )

    failed_reminders_task = asyncio.create_task(
        failed_reminders_consume.consume(
            partial(failed_reminders_callback, AsyncSessionLocal)
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
