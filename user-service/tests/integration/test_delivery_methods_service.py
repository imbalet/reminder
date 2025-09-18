from uuid import uuid4

import pytest

from user_service.exceptions import AlreadyExistsError
from user_service.schemas import (
    DeliveryMethodEnum,
    DeliveryMethodResponse,
    MetaData,
    User,
)
from user_service.services import DeliveryMethodsService


@pytest.fixture
async def sample_method(
    sample_user: User, delivery_methods_service: DeliveryMethodsService
):
    return await delivery_methods_service.add(
        sample_user.id,
        DeliveryMethodEnum.TELEGRAM,
        "chat_id",
        meta_data=MetaData(username=""),
    )


# ------------------------------------#
#               TESTS                 #
# ------------------------------------#


@pytest.mark.asyncio
async def test_valid_add_get(
    delivery_methods_service: DeliveryMethodsService, sample_user: User
):
    res = await delivery_methods_service.add(
        sample_user.id, DeliveryMethodEnum.TELEGRAM, "tg_nickname"
    )
    from_db = await delivery_methods_service.get(res.id)
    assert from_db is not None
    assert from_db == res
    assert from_db.contact_value == "tg_nickname"
    assert from_db.delivery_method == DeliveryMethodEnum.TELEGRAM


@pytest.mark.asyncio
async def test_method_already_exists_add(
    delivery_methods_service: DeliveryMethodsService, sample_user: User
):
    await delivery_methods_service.add(
        sample_user.id, DeliveryMethodEnum.TELEGRAM, "tg_nickname"
    )
    with pytest.raises(AlreadyExistsError):
        await delivery_methods_service.add(
            sample_user.id, DeliveryMethodEnum.TELEGRAM, "tg_nickname"
        )


@pytest.mark.asyncio
async def test_valid_remove(
    sample_user: User,
    sample_method: DeliveryMethodResponse,
    delivery_methods_service: DeliveryMethodsService,
):
    deleted = await delivery_methods_service.delete(sample_user.id, sample_method.id)
    res = await delivery_methods_service.get(sample_method.id)

    assert deleted is not None
    assert res is None


@pytest.mark.asyncio
async def test_forbidden_remove(
    sample_method: DeliveryMethodResponse,
    delivery_methods_service: DeliveryMethodsService,
):
    deleted = await delivery_methods_service.delete(uuid4(), sample_method.id)
    res = await delivery_methods_service.get(sample_method.id)

    assert deleted is None
    assert res is not None


@pytest.mark.asyncio
async def test_method_not_exists_remove(
    sample_user: User,
    delivery_methods_service: DeliveryMethodsService,
):
    deleted = await delivery_methods_service.delete(sample_user.id, uuid4())

    assert deleted is None


@pytest.mark.asyncio
async def test_valid_get_all(
    sample_user: User,
    delivery_methods_service: DeliveryMethodsService,
):
    await delivery_methods_service.add(
        sample_user.id, DeliveryMethodEnum.EMAIL, "email", meta_data=None
    )
    await delivery_methods_service.add(
        sample_user.id, DeliveryMethodEnum.EMAIL, "email1", meta_data=None
    )
    res = await delivery_methods_service.get_all(sample_user.id)

    assert len(res) == 2


@pytest.mark.asyncio
async def test_empty_get_all(
    sample_user: User,
    delivery_methods_service: DeliveryMethodsService,
):
    res = await delivery_methods_service.get_all(sample_user.id)

    assert len(res) == 0
