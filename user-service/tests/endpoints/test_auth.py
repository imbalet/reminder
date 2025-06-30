from httpx import AsyncClient
import pytest

from src.schemas import UserRegisterRequset, UserAuth, UserResponse, TokenResponse


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
