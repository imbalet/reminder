from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from auth_service.schemas import (
    TokenResponse,
    UserAuth,
    UserResponse,
    UserRegisterRequset,
)
from auth_service.main import app
from auth_service.dependencies import (
    get_async_session_factory,
    get_security_service,
    get_user_register_event_service,
    get_channel_pool,
)
from auth_service.services import SecurityService


@pytest.fixture
async def async_client(async_session_factory):
    app.dependency_overrides[get_async_session_factory] = lambda: async_session_factory
    app.dependency_overrides[get_security_service] = lambda: SecurityService(
        Path(".secrets")
    )
    app.dependency_overrides[get_channel_pool] = lambda: AsyncMock()
    app.dependency_overrides[get_user_register_event_service] = (
        lambda: AsyncMock()
    )  # mock for sending data to rabbitmq
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def sample_register_user_data():
    return UserRegisterRequset(
        name="john",
        email="john@example.com",
        password="password",
    )


@pytest.fixture
def sample_auth_user_data():
    return UserAuth(
        email="john@example.com",
        password="password",
    )


@pytest.fixture
async def registered_user(
    async_client: AsyncClient, sample_register_user_data: UserRegisterRequset
):
    response = await async_client.post(
        "/api/auth/register", json=sample_register_user_data.model_dump()
    )
    assert response.status_code == 200
    return UserResponse.model_validate(response.json())


@pytest.fixture
async def authenticated_user(
    async_client: AsyncClient,
    registered_user: UserResponse,
    sample_auth_user_data: UserAuth,
):
    response = await async_client.post(
        "/api/auth/login",
        data={
            "username": sample_auth_user_data.email,
            "password": sample_auth_user_data.password,
        },
    )
    assert response.cookies["refresh_token"] is not None
    assert response.status_code == 200
    return (
        TokenResponse.model_validate(response.json()),
        response.cookies["refresh_token"],
    )
