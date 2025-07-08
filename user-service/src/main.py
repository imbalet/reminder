import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config
from src.database import create_tables
from src.exceptions import AppException
from src.exception_handler import exception_handler
from src.api import delivery_methods_router
from src.event_handler import consume

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

    logger.info("DB started")

    task = asyncio.create_task(
        consume(config.RMQ_URL, config.RMQ_EVENTS_QUEUE, AsyncSessionLocal)
    )
    logger.info("Consume task started")
    yield
    task.cancel()
    try:
        await task
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
