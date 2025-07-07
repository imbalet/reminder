from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio.session import async_sessionmaker, AsyncSession
from src.services import UserService
from src.schemas import UserResponse
from src.exceptions import AlreadyExistsError


@pytest.fixture
async def sample_user(async_session_factory: async_sessionmaker[AsyncSession]):
    service = UserService(async_session_factory)
    res = await service.create_user(
        name="john", email="john@example.com", hashed_password="hash"
    )
    return UserResponse.model_validate(res, from_attributes=True)


# ------------------------------------#
#               TESTS                 #
# ------------------------------------#


@pytest.mark.asyncio
async def test_valid_creating_user(user_service: UserService):
    created = await user_service.create_user(
        name="john", email="john@example.com", hashed_password="hash"
    )
    assert await user_service.get_user(created.id) is not None


@pytest.mark.asyncio
async def test_email_already_in_use_creating_user(user_service: UserService):
    await user_service.create_user(
        name="john", email="john@example.com", hashed_password="hash"
    )
    with pytest.raises(AlreadyExistsError):
        await user_service.create_user(
            name="john", email="john@example.com", hashed_password="hash"
        )


@pytest.mark.asyncio
async def test_valid_get_user_by_id(
    user_service: UserService, sample_user: UserResponse
):
    res = await user_service.get_user(sample_user.id)
    assert res is not None
    assert res.email == sample_user.email
    assert res.id == sample_user.id


@pytest.mark.asyncio
async def test_user_not_exists_get_user_by_id(user_service: UserService):
    res = await user_service.get_user(uuid4())
    assert res is None


@pytest.mark.asyncio
async def test_valid_get_user_by_email(
    user_service: UserService, sample_user: UserResponse
):
    res = await user_service.get_user_by_email(sample_user.email)
    assert res is not None
    assert res.email == sample_user.email
    assert res.id == sample_user.id


@pytest.mark.asyncio
async def test_user_not_exists_get_user_by_email(user_service: UserService):
    res = await user_service.get_user_by_email("email")
    assert res is None
