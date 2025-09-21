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


@pytest.fixture
async def async_client(
    async_session_factory,
    mock_delivery_service,
    mock_confirm_service,
    mock_produce_service,
    mock_notification_service,
):
    app.dependency_overrides.update(
        {
            get_async_session_factory: lambda: async_session_factory,
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
