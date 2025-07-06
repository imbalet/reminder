import asyncio
import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio.session import async_sessionmaker, AsyncSession

from src.models import RefreshTokensOrm
from src.services import RefreshTokenService, UserService
from src.schemas import UserResponse, RefreshTokenData
from src.exceptions import NotFoundError, AlreadyExistsError


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


# ------------------------------------#
#               TESTS                 #
# ------------------------------------#


@pytest.mark.asyncio
async def test_valid_save_token(token_service: RefreshTokenService, sample_token_data):
    await token_service.save(*sample_token_data)


@pytest.mark.asyncio
async def test_user_not_exists_save_token(
    token_service: RefreshTokenService, sample_token_data
):
    sample_token_data = list(sample_token_data)
    sample_token_data[3] = uuid4()
    with pytest.raises(NotFoundError):
        await token_service.save(*sample_token_data)


@pytest.mark.asyncio
async def test_token_already_exists_save_token(
    token_service: RefreshTokenService, sample_token_data
):
    await token_service.save(*sample_token_data)
    with pytest.raises(AlreadyExistsError):
        await token_service.save(*sample_token_data)


@pytest.mark.asyncio
async def test_valid_find_token(
    token_service: RefreshTokenService, sample_token: RefreshTokenData
):
    res = await token_service.find_by_jti(sample_token.jti)
    assert res is not None
    assert res.user_id == sample_token.user_id


@pytest.mark.asyncio
async def test_not_found_find_token(token_service: RefreshTokenService):
    res = await token_service.find_by_jti(uuid4())
    assert res is None


@pytest.mark.asyncio
async def test_expired_find_token(
    token_service: RefreshTokenService,
    async_session_factory: async_sessionmaker[AsyncSession],
    sample_token_data,
):
    sample_token_data = list(sample_token_data)
    sample_token_data[2] = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
        hours=1
    )
    await token_service.save(*sample_token_data)
    async with async_session_factory() as session:
        res = await session.get(RefreshTokensOrm, sample_token_data[0])
        assert res is not None
    res = await token_service.find_by_jti(sample_token_data[0])
    assert res is None
    await asyncio.sleep(0.5)
    async with async_session_factory() as session:
        res = await session.get(RefreshTokensOrm, sample_token_data[0])
        assert res is None


@pytest.mark.asyncio
async def test_valid_revoke_token(token_service: RefreshTokenService, sample_token):
    await token_service.revoke_token(sample_token.jti)
    res = await token_service.find_by_jti(sample_token.jti)
    assert res is None


@pytest.mark.asyncio
async def test_not_found_revoke_token(token_service: RefreshTokenService):
    await token_service.revoke_token(uuid4())


@pytest.mark.asyncio
async def test_valid_revoke_for_user_token(
    token_service: RefreshTokenService, sample_token
):
    await token_service.revoke_for_user(sample_token.user_id)
    res = await token_service.find_by_jti(sample_token.jti)
    assert res is None


@pytest.mark.asyncio
async def test_user_not_exists_revoke_for_user_token(
    token_service: RefreshTokenService,
):
    await token_service.revoke_for_user(uuid4())
