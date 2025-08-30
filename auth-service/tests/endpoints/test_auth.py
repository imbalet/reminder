from httpx import AsyncClient
import pytest

from auth_service.schemas import (
    UserRegisterRequset,
    UserAuth,
    UserResponse,
    TokenResponse,
)


@pytest.mark.asyncio
async def test_valid_register(
    async_client: AsyncClient, sample_register_user_data: UserRegisterRequset
):
    response = await async_client.post(
        "/api/auth/register", json=sample_register_user_data.model_dump()
    )
    assert response.status_code == 200
    res = UserResponse.model_validate(response.json())
    assert res.email == sample_register_user_data.email


@pytest.mark.asyncio
async def test_valid_login(
    async_client: AsyncClient,
    sample_auth_user_data: UserAuth,
    registered_user: UserResponse,
):
    response = await async_client.post(
        "/api/auth/login",
        data={
            "username": sample_auth_user_data.email,
            "password": sample_auth_user_data.password,
        },
    )
    assert response.status_code == 200
    res = TokenResponse.model_validate(response.json())
    assert res.token_type.lower() == "bearer"
    assert "set-cookie" in response.headers
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_valid_refresh(
    async_client: AsyncClient,
    authenticated_user: tuple[TokenResponse, str],
):
    _, refresh_token = authenticated_user
    response = await async_client.post(
        "/api/auth/refresh", cookies={"refresh_token": refresh_token}
    )
    res = TokenResponse.model_validate(response.json())
    assert response.status_code == 200
    assert "set-cookie" in response.headers
    assert "refresh_token" in response.cookies
    assert res.token_type.lower() == "bearer"


@pytest.mark.asyncio
async def test_valid_logout(
    async_client: AsyncClient,
    authenticated_user: tuple[TokenResponse, str],
):
    _, refresh_token = authenticated_user
    response = await async_client.post(
        "/api/auth/logout", cookies={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert "set-cookie" in response.headers
    assert "refresh_token" not in response.cookies
