import aio_pika
from aio_pika.pool import Pool
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


from src.models import Base
from src.services import ReminderService, EventService
from tests.config import config


@pytest.fixture
async def async_session_factory():
    engine = create_async_engine(
        config.DB_URL,
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
def rmq_channel_pool():
    async def create_connection():
        return await aio_pika.connect_robust(config.RMQ_URL)

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
def send_service(rmq_channel_pool):
    return EventService(rmq_channel_pool, config.TEST_RMQ_ROUTING_KEY)
