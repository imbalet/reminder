from uuid import uuid4

import pytest

from user_service.exceptions import AlreadyExistsError
from user_service.schemas import (
    DeliveryMethodEnum,
    DeliveryMethodResponse,
    User,
)
from user_service.services import DeliveryMethodsService


@pytest.mark.asyncio
async def test_create_get(
    delivery_methods_service: DeliveryMethodsService, sample_user_db: User
):
    res = await delivery_methods_service.create(
        sample_user_db.id, DeliveryMethodEnum.TELEGRAM, "tg_nickname"
    )
    from_db = await delivery_methods_service.get(res.id)
    assert from_db is not None
    assert from_db == res
    assert from_db.contact_value == "tg_nickname"
    assert from_db.delivery_method == DeliveryMethodEnum.TELEGRAM


@pytest.mark.asyncio
async def test_create_method_already_exists(
    delivery_methods_service: DeliveryMethodsService, sample_user_db: User
):
    await delivery_methods_service.create(
        sample_user_db.id, DeliveryMethodEnum.TELEGRAM, "tg_nickname"
    )
    with pytest.raises(AlreadyExistsError):
        await delivery_methods_service.create(
            sample_user_db.id, DeliveryMethodEnum.TELEGRAM, "tg_nickname"
        )


@pytest.mark.asyncio
async def test_delete(
    delivery_methods_service: DeliveryMethodsService,
    sample_user_db: User,
    sample_method_tg_db: DeliveryMethodResponse,
):
    deleted = await delivery_methods_service.delete(
        sample_user_db.id, sample_method_tg_db.id
    )
    res = await delivery_methods_service.get(sample_method_tg_db.id)

    assert deleted is not None
    assert res is None


@pytest.mark.asyncio
async def test_remove_forbidden(
    delivery_methods_service: DeliveryMethodsService,
    sample_method_tg_db: DeliveryMethodResponse,
):
    deleted = await delivery_methods_service.delete(uuid4(), sample_method_tg_db.id)
    res = await delivery_methods_service.get(sample_method_tg_db.id)

    assert deleted is None
    assert res is not None


@pytest.mark.asyncio
async def test_remove_method_not_exists(
    delivery_methods_service: DeliveryMethodsService,
    sample_user_db: User,
):
    deleted = await delivery_methods_service.delete(sample_user_db.id, uuid4())

    assert deleted is None


@pytest.mark.asyncio
async def test_get_all(
    delivery_methods_service: DeliveryMethodsService,
    sample_user_db: User,
):
    await delivery_methods_service.create(
        sample_user_db.id, DeliveryMethodEnum.EMAIL, "email", meta_data=None
    )
    await delivery_methods_service.create(
        sample_user_db.id, DeliveryMethodEnum.EMAIL, "email1", meta_data=None
    )
    paged_items = await delivery_methods_service.get_all(
        sample_user_db.id, page=1, page_size=100
    )

    assert len(paged_items.items) == 2


@pytest.mark.asyncio
async def test_get_all_empty(
    delivery_methods_service: DeliveryMethodsService,
    sample_user_db: User,
):
    paged_items = await delivery_methods_service.get_all(
        sample_user_db.id, page=1, page_size=100
    )
    assert len(paged_items.items) == 0


@pytest.mark.parametrize(
    "count, page_size, page, expect_count",
    [
        (1, 1, 1, 1),
        (2, 1, 1, 1),
        (10, 10, 1, 10),
        (10, 5, 2, 5),
        (2, 10, 1, 2),
    ],
)
async def test_get_all_pagination(
    delivery_methods_service: DeliveryMethodsService,
    sample_user_db: User,
    count: int,
    page_size: int,
    page: int,
    expect_count: int,
):
    methods = [
        await delivery_methods_service.create(
            sample_user_db.id, DeliveryMethodEnum.EMAIL, f"email{i}", meta_data=None
        )
        for i in range(count)
    ]

    paged_items = await delivery_methods_service.get_all(
        sample_user_db.id, page=page, page_size=page_size
    )

    assert len(paged_items.items) == expect_count
    assert paged_items.items == methods[((page - 1) * page_size) :][:page_size]
