import asyncio
import logging
from contextlib import asynccontextmanager

import aio_pika
from fastapi import FastAPI
from redis import asyncio as aioredis

from user_service.config import config
from user_service.database import init_database
from user_service.tasks import setup_tasks

logger = logging.getLogger(__name__)


def get_channel_pools():
    async def create_connection():
        return await aio_pika.connect_robust(config.RMQ_URL)

    connection_pool = aio_pika.pool.Pool(create_connection, max_size=10)

    async def create_channel():
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool = aio_pika.pool.Pool(create_channel, max_size=100)
    return connection_pool, channel_pool


def setup_redis():
    redis = aioredis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        db=0,
        max_connections=20,
    )
    return redis


@asynccontextmanager
async def startup_event(app: FastAPI):
    app.state.db_engine, app.state.session_factory = await init_database()
    app.state.connection_pool, app.state.channel_pool = get_channel_pools()
    app.state.redis = setup_redis()

    logger.info("DB started")

    consume_users_task, consume_failed_reminders_task = await setup_tasks(
        app.state.channel_pool, app.state.session_factory
    )

    logger.info("Consume tasks started")
    yield
    consume_users_task.cancel()
    try:
        await consume_users_task
    except asyncio.CancelledError:
        pass

    consume_failed_reminders_task.cancel()
    try:
        await consume_failed_reminders_task
    except asyncio.CancelledError:
        pass

    await app.state.channel_pool.close()
    await app.state.connection_pool.close()
    await app.state.db_engine.dispose()
    await app.state.redis.close()

    logger.info("App stopped")
