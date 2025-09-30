from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from user_service.config import Config, LogLevels
from user_service.schemas import User


@pytest.fixture(autouse=True, scope="session")
def patch_config_module():
    fake_config = Config.model_construct(
        LOG_LEVEL=LogLevels("DEBUG"),
        DB_HOST="localhost",
        DB_PORT=5432,
        DB_NAME="test",
        DB_USER="user",
        DB_PASS="pass",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_PASSWORD="",
        RMQ_DLQ_FAILED_REMINDERS_NAME="dlq",
        RMQ_DLX_FAILED_REMINDERS_NAME="dlx",
        RMQ_USER_ADD_QUEUE="q1",
        RMQ_DELIVERY_METHOD_ADD_QUEUE="q2",
        RMQ_DELIVERY_METHOD_REMOVE_QUEUE="q3",
        RMQ_REMINDER_DEACTIVATE_QUEUE="q4",
        RMQ_USER="guest",
        RMQ_PASS="guest",
        RMQ_HOST="localhost",
        RMQ_PORT="5672",
    )
    with patch("user_service.config.Config", return_value=fake_config), patch(
        "user_service.config.config", fake_config
    ):
        yield


@asynccontextmanager
async def fake_lifespan(app):
    yield


@pytest.fixture
def user_header(user_data: User) -> dict:
    return {"app-user-id": str(user_data.id)}


@pytest.fixture
async def async_client(
    mock_async_session_factory,
    mock_delivery_service,
    mock_confirm_service,
    mock_produce_service,
    mock_notification_service,
):
    from user_service.dependencies import (
        get_add_delivery_method_produce_service,
        get_async_session_factory,
        get_confirm_code_service,
        get_delivery_methods_service,
        get_notification_service,
        get_remove_delivery_method_produce_service,
    )
    from user_service.main import app

    app.dependency_overrides.update(
        {
            get_async_session_factory: lambda: mock_async_session_factory,
            get_delivery_methods_service: lambda: mock_delivery_service,
            get_confirm_code_service: lambda: mock_confirm_service,
            get_add_delivery_method_produce_service: lambda: mock_produce_service,
            get_remove_delivery_method_produce_service: lambda: mock_produce_service,
            get_notification_service: lambda: mock_notification_service,
        }
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
