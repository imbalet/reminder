import asyncio
import logging
from contextlib import asynccontextmanager

import aio_pika
from fastapi import FastAPI

from reminder_service.config import config
from reminder_service.database import init_database
from reminder_service.tasks import setup_tasks

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

    app.state.connection_pool, app.state.channel_pool = get_channel_pools()
    app.state.db_engine, app.state.session_factory = await init_database()

    logger.info("DB started")

    send_reminder_task_scheduler, consume_error_reminders_task = await setup_tasks(
        channel_pool=app.state.channel_pool,
        session_factory=app.state.session_factory,
    )

    yield
    send_reminder_task_scheduler.shutdown(wait=False)
    consume_error_reminders_task.cancel()
    try:
        await consume_error_reminders_task
    except asyncio.CancelledError:
        pass

    await app.state.channel_pool.close()
    await app.state.connection_pool.close()
    await app.state.db_engine.dispose()

    logger.info("App stopped")
