import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.dependencies import (
    get_async_session_factory,
    get_delivery_methods_service,
    get_confirm_code_service,
)


@pytest.fixture
async def async_client(
    async_session_factory, mock_delivery_service, mock_confirm_service
):
    app.dependency_overrides.update(
        {
            get_async_session_factory: lambda: async_session_factory,
            get_delivery_methods_service: lambda: mock_delivery_service,
            get_confirm_code_service: lambda: mock_confirm_service,
        }
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
