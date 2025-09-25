from uuid import uuid4

import pytest

from user_service.schemas import NotificationResponse, UserResponse
from user_service.services import NotificationService


async def test_create_get(
    notification_service: NotificationService,
    sample_user_db: UserResponse,
    notification_data: NotificationResponse,
):
    res = await notification_service.create(
        user_id=sample_user_db.id,
        title=notification_data.title,
        content=notification_data.content,
    )
    from_db = await notification_service.get(res.id)
    assert res == from_db


async def test_delete(
    notification_service: NotificationService,
    sample_user_db: UserResponse,
    sample_notification_db: NotificationResponse,
):
    deleted = await notification_service.delete(
        sample_notification_db.id, sample_user_db.id
    )
    res = await notification_service.get(sample_notification_db.id)

    assert deleted is not None
    assert res is None


async def test_remove_forbidden(
    notification_service: NotificationService,
    sample_notification_db: NotificationResponse,
):
    deleted = await notification_service.delete(sample_notification_db.id, uuid4())
    res = await notification_service.get(sample_notification_db.id)

    assert deleted is None
    assert res is not None


@pytest.mark.asyncio
async def test_remove_not_exists(
    notification_service: NotificationService, sample_user_db: UserResponse
):
    deleted = await notification_service.delete(uuid4(), sample_user_db.id)

    assert deleted is None


async def test_get_all(
    notification_service: NotificationService,
    sample_user_db: UserResponse,
    notification_data: NotificationResponse,
):
    await notification_service.create(
        user_id=sample_user_db.id,
        title=notification_data.title,
        content=notification_data.content,
    )
    await notification_service.create(
        user_id=sample_user_db.id,
        title=notification_data.title,
        content=notification_data.content,
    )
    paged_items = await notification_service.get_all(
        sample_user_db.id, page=1, page_size=100
    )

    assert len(paged_items.items) == 2


async def test_get_all_empty(
    notification_service: NotificationService, sample_user_db: UserResponse
):
    paged_items = await notification_service.get_all(
        sample_user_db.id, page=1, page_size=100
    )
    assert len(paged_items.items) == 0


async def test_read(
    notification_service: NotificationService,
    sample_notification_db: NotificationResponse,
):
    res = await notification_service.read(
        sample_notification_db.id, sample_notification_db.user_id
    )

    from_db = await notification_service.get(sample_notification_db.id)

    assert sample_notification_db.is_read is False
    assert res is not None
    assert res.is_read is True
    assert from_db and from_db.is_read is True


async def test_read_not_found(
    notification_service: NotificationService, sample_user_db: UserResponse
):
    res = await notification_service.read(uuid4(), sample_user_db.id)
    assert res is None


async def test_read_other_user(
    notification_service: NotificationService,
    sample_notification_db: NotificationResponse,
):
    res = await notification_service.read(sample_notification_db.id, uuid4())
    from_db = await notification_service.get(sample_notification_db.id)

    assert sample_notification_db.is_read is False
    assert res is None
    assert from_db and from_db.is_read is False
