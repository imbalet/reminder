import pytest
from httpx import ASGITransport, AsyncClient

from user_service.dependencies import (
    get_add_delivery_method_produce_service,
    get_async_session_factory,
    get_confirm_code_service,
    get_delivery_methods_service,
    get_notification_service,
    get_remove_delivery_method_produce_service,
)
from user_service.main import app
from user_service.schemas import User


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
