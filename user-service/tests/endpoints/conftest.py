import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.dependencies import get_async_session_factory


@pytest.fixture
async def async_client(async_session_factory):
    app.dependency_overrides[get_async_session_factory] = lambda: async_session_factory
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
