import pytest
from httpx import ASGITransport, AsyncClient

from reminder_service.dependencies import (
    get_async_session_factory,
    get_reminders_service,
)
from reminder_service.main import app


@pytest.fixture
def user_header(user_id) -> dict:
    return {"app-user-id": str(user_id)}


@pytest.fixture
async def async_client(mock_async_session_factory, mock_reminder_service):
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
