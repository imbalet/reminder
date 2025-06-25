import datetime
from uuid import uuid4
import pytest
from sqlalchemy.ext.asyncio.session import async_sessionmaker, AsyncSession
from src.services.token_service import RefreshTokenService
from src.services.user_service import UserService
from src.schemas.user import UserResponse


@pytest.fixture
async def sample_user(async_session_factory: async_sessionmaker[AsyncSession]):
    service = UserService(async_session_factory)
    res = await service.create_user(
        name="john", email="john@example.com", hashed_password="hash"
    )
    return UserResponse.model_validate(res, from_attributes=True)


@pytest.fixture
def sample_token_data(sample_user: UserResponse):
    jti = uuid4()
    token_hash = "hash"
    expiration_time = datetime.datetime.now(tz=None) + datetime.timedelta(days=1)
    user_id = sample_user.id

    return jti, token_hash, expiration_time, user_id


@pytest.fixture
async def sample_token(
    async_session_factory: async_sessionmaker[AsyncSession], sample_token_data
):
    service = RefreshTokenService(async_session_factory)
    res = await service.save(*sample_token_data)
    return res


@pytest.mark.asyncio
async def test_valid_save_token(
    async_session_factory: async_sessionmaker[AsyncSession], sample_token_data
):
    service = RefreshTokenService(async_session_factory)
    res = await service.save(*sample_token_data)


@pytest.mark.asyncio
async def test_valid_find_token(
    async_session_factory: async_sessionmaker[AsyncSession], sample_token
):
    service = RefreshTokenService(async_session_factory)
    res = await service.find_by_jti(sample_token.jti)
    assert res is not None
    assert res.user_id == sample_token.user_id


@pytest.mark.asyncio
async def test_valid_revoke_token(
    async_session_factory: async_sessionmaker[AsyncSession], sample_token
):
    service = RefreshTokenService(async_session_factory)
    await service.revoke_token(sample_token.jti)
    res = await service.find_by_jti(sample_token.jti)
    assert res is None


@pytest.mark.asyncio
async def test_valid_revoke_for_user_token(
    async_session_factory: async_sessionmaker[AsyncSession], sample_token
):
    service = RefreshTokenService(async_session_factory)
    await service.revoke_for_user(sample_token.user_id)
    res = await service.find_by_jti(sample_token.jti)
    assert res is None
