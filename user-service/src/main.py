from contextlib import asynccontextmanager
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import config
from src.database import create_tables
from src.api import auth_router, jwks_router
from src.services import SecurityService
from src.models import RefreshTokensOrm

scheduler = AsyncIOScheduler()


async def delete_expired_tokens(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        try:
            stmt = delete(RefreshTokensOrm).where(
                RefreshTokensOrm.expires_at <= datetime.now(timezone.utc)
            )
            result = await session.execute(stmt)
            await session.commit()
            print(f"Удалено {result.rowcount} токенов")
        except Exception as e:
            print(f"Ошибка удаления токенов: {e}")
            await session.rollback()


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
    app.state.security_service = SecurityService.load_keys()

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


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(auth_router)
app.include_router(jwks_router)
