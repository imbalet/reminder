import os

import aio_pika
from aio_pika.pool import Pool
import dotenv
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


from src.models import Base
from src.services import ReminderService, SendService


@pytest.fixture
async def async_session_factory():
    dotenv.load_dotenv("tests/.env.test")

    DB_USER = os.getenv("TEST_DB_USER")
    DB_PASS = os.getenv("TEST_DB_PASS")
    DB_NAME = os.getenv("TEST_DB_NAME")
    DB_HOST = os.getenv("TEST_DB_HOST")
    DB_PORT = os.getenv("TEST_DB_PORT")

    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    engine = create_async_engine(
        DB_URL,
        echo=True,
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

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield AsyncSessionLocal

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def channel_pool():
    async def create_connection():
        return await aio_pika.connect_robust("amqp://user:dev_password@localhost/")

    async def create_channel():
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    connection_pool = Pool(create_connection, max_size=10)
    channel_pool = Pool(create_channel, max_size=100)
    return channel_pool


@pytest.fixture
def reminder_service(async_session_factory):
    return ReminderService(async_session_factory)


@pytest.fixture
def send_service(async_session_factory, channel_pool):
    return SendService(async_session_factory, channel_pool)
