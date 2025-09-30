from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from reminder_service.config import Config, LogLevels


@pytest.fixture
def user_header(user_id) -> dict:
    return {"app-user-id": str(user_id)}


@pytest.fixture(autouse=True, scope="session")
def patch_config_module():
    fake_config = Config.model_construct(
        LOG_LEVEL=LogLevels("DEBUG"),
        DB_HOST="localhost",
        DB_PORT=5432,
        DB_NAME="test",
        DB_USER="user",
        DB_PASS="pass",
        RMQ_DLQ_FAILED_REMINDERS_NAME="dlq",
        RMQ_DLX_FAILED_REMINDERS_NAME="dlx",
        RMQ_DELIVERY_METHOD_ADD_QUEUE="q1",
        RMQ_DELIVERY_METHOD_REMOVE_QUEUE="q2",
        RMQ_REMINDER_DEACTIVATE_QUEUE="q3",
        RMQ_REMINDERS_QUEUE="q4",
        RMQ_USER="guest",
        RMQ_PASS="guest",
        RMQ_HOST="localhost",
        RMQ_PORT="5672",
    )
    with patch("reminder_service.config.Config", return_value=fake_config), patch(
        "reminder_service.config.config", fake_config
    ):
        yield


@pytest.fixture
async def async_client(mock_async_session_factory, mock_reminder_service):
    from reminder_service.dependencies import (
        get_async_session_factory,
        get_reminders_service,
    )
    from reminder_service.main import app

    app.dependency_overrides.update(
        {
            get_async_session_factory: lambda: mock_async_session_factory,
            get_reminders_service: lambda: mock_reminder_service,
        }
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
