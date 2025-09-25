from uuid import uuid4

import pytest

from user_service.exceptions import AlreadyExistsError
from user_service.schemas import User
from user_service.services import UserService


@pytest.mark.asyncio
async def test_create(user_service: UserService, user_data: User):
    res = await user_service.create(user_data.id, user_data.name, user_data.email)
    assert res.id == user_data.id


@pytest.mark.asyncio
async def test_create_already_exists(user_service: UserService, sample_user_db: User):
    with pytest.raises(AlreadyExistsError):
        await user_service.create(
            sample_user_db.id, sample_user_db.name, sample_user_db.email
        )


@pytest.mark.asyncio
async def test_get(user_service: UserService, sample_user_db: User):
    res = await user_service.get(sample_user_db.id)
    assert res is not None
    assert res.id == sample_user_db.id


@pytest.mark.asyncio
async def test_get_empty(user_service: UserService):
    res = await user_service.get(uuid4())
    assert res is None
