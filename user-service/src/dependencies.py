from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.services import (
    DeliveryMethodsService,
)


def get_async_session_factory(req: Request):
    return req.app.state.session_factory  # type: ignore


def get_delivery_methods_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> DeliveryMethodsService:
    return DeliveryMethodsService(session_factory)
