from contextlib import asynccontextmanager
import logging
from pathlib import Path

import aio_pika
from fastapi import FastAPI

from auth_service.config import config
from auth_service.services import SecurityService
from auth_service.database import init_database
from auth_service.tasks import setup_tasks

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


@asynccontextmanager
async def startup_event(app: FastAPI):
    app.state.db_engine, app.state.session_factory = await init_database()
    app.state.security_service = SecurityService(secret_path=Path(".secrets"))
    app.state.connection_pool, app.state.channel_pool = get_channel_pools()

    delete_expired_tokens_task_scheduler = setup_tasks(app.state.session_factory)
    logger.info("DB started")

    yield

    delete_expired_tokens_task_scheduler.shutdown()

    await app.state.channel_pool.close()
    await app.state.connection_pool.close()
    await app.state.db_engine.dispose()

    logger.info("App stopped")
