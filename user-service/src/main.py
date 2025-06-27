from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


from src.dependencies import get_security_service
from src.config import config
from src.database import create_tables
from src.api import auth_router, protected_router
from src.services import SecurityService


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
    yield


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(auth_router)
app.include_router(protected_router)


@app.get("/.well-known/jwks.json", response_class=JSONResponse)
async def get_jwks(
    security_servise: Annotated[SecurityService, Depends(get_security_service)],
) -> dict:
    """Эндпоинт для отдачи JWKS"""
    return security_servise.get_jwks()
