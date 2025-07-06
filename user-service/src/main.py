from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config
from src.database import create_tables
from src.exceptions import AppException
from src.exception_handler import exception_handler
from src.api import delivery_methods_router


@asynccontextmanager
async def startup_event(app: FastAPI):
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

    await create_tables(engine)
    app.state.session_factory = AsyncSessionLocal

    yield


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(delivery_methods_router)

app.add_exception_handler(AppException, exception_handler)
