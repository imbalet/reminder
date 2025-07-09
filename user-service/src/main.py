import asyncio
from contextlib import asynccontextmanager
import logging

import aio_pika
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config
from src.database import create_tables
from src.exceptions import AppException
from src.exception_handler import exception_handler
from src.api import delivery_methods_router
from src.event_handler import add_user_callback, confirm_method_callback
from src.services import EventService

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL.value)

console_handler = logging.StreamHandler()
console_handler.setLevel(config.LOG_LEVEL.value)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(config.LOG_LEVEL.value)


formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


logging.getLogger("uvicorn").handlers = logger.handlers
logging.getLogger("uvicorn.access").handlers = logger.handlers
logging.getLogger("fastapi").handlers = logger.handlers


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

    add_user_service = EventService(app.state.channel_pool, config.RMQ_USER_ADD_QUEUE)
    confirm_method_service = EventService(
        app.state.channel_pool, config.RMQ_METHOD_CONFIRM_QUEUE
    )

    confirm_methods_task = asyncio.create_task(
        confirm_method_service.consume(
            async_callback=confirm_method_callback, session_factory=AsyncSessionLocal
        )
    )

    add_users_task = asyncio.create_task(
        add_user_service.consume(
            async_callback=add_user_callback, session_factory=AsyncSessionLocal
        )
    )

    logger.info("Consume tasks started")
    yield
    add_users_task.cancel()
    confirm_methods_task.cancel()
    try:
        await add_users_task
    except asyncio.CancelledError:
        pass
    logger.info("App stopped")


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(delivery_methods_router)

app.add_exception_handler(AppException, exception_handler)
