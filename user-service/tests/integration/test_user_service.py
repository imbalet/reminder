import pytest

from user_service.schemas import User
from user_service.services import UserService


@pytest.mark.asyncio
async def test_valid_add(sample_user_data: User, user_service: UserService):
    res = await user_service.create(
        sample_user_data.id, sample_user_data.name, sample_user_data.email
    )
    assert res.id == sample_user_data.id


@pytest.mark.asyncio
async def test_valid_get(sample_user: User, user_service: UserService):
    res = await user_service.get(sample_user.id)
    assert res is not None
    assert res.id == sample_user.id
