from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from pathlib import Path

import aio_pika
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config
from src.database import create_tables
from src.services import SecurityService
from src.models import RefreshTokensOrm

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


async def delete_expired_tokens(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        try:
            stmt = delete(RefreshTokensOrm).where(
                RefreshTokensOrm.expires_at <= datetime.now(timezone.utc)
            )
            result = await session.execute(stmt)
            await session.commit()
            logger.info(f"Deleted {result.rowcount} expired tokens")
        except Exception as e:
            logger.error("Error deleting tokens", exc_info=e)
            await session.rollback()


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
    app.state.security_service = SecurityService(secret_path=Path(".secrets"))
    app.state.channel_pool = get_channel_pool()
    logger.info("DB started")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        delete_expired_tokens,
        "interval",
        hours=3,
        args=[app.state.session_factory],
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()

    yield

    scheduler.shutdown()
    logger.info("App stopped")
