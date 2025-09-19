import datetime
import zoneinfo
from uuid import uuid4

import pytest

from reminder_service.schemas import (
    ReminderEdit,
    ReminderResponse,
)
from reminder_service.services import ReminderService

# ------------------------------------#
#               TESTS                 #
# ------------------------------------#


@pytest.mark.asyncio
async def test_valid_creating(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram,
    sample_db_delivery_method_email,
):
    created = await reminder_service.create_reminder(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=datetime.datetime.now() + datetime.timedelta(days=1),
        delivery_method_ids=[
            sample_db_delivery_method_telegram.id,
            sample_db_delivery_method_email.id,
        ],
    )
    assert await reminder_service.get_reminder(created.id) is not None


@pytest.mark.asyncio
async def test_valid_creating_not_utc(
    reminder_service: ReminderService, sample_db_delivery_method_email
):
    time = datetime.datetime.now(
        zoneinfo.ZoneInfo("Europe/Moscow")
    ) + datetime.timedelta(days=1)
    created = await reminder_service.create_reminder(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=time,
        delivery_method_ids=[
            sample_db_delivery_method_email.id,
        ],
    )
    res = await reminder_service.get_reminder(created.id)
    assert res is not None
    assert res.remind_date == time


@pytest.mark.asyncio
async def test_valid_get(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.get_reminder(sample_db_reminder.id)
    assert res is not None
    assert res == sample_db_reminder


@pytest.mark.asyncio
async def test_not_exists_get(reminder_service: ReminderService):
    res = await reminder_service.get_reminder(uuid4())
    assert res is None


@pytest.mark.asyncio
async def test_valid_get_by_user_id(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.get_reminders_by_user_id(sample_db_reminder.user_id)
    assert res is not None
    assert res[0] == sample_db_reminder


@pytest.mark.asyncio
async def test_valid_get_by_user_id_multiply(
    reminder_service: ReminderService,
    sample_db_reminder: ReminderResponse,
    sample_db_delivery_method_email,
):
    for _ in range(3):
        await reminder_service.create_reminder(
            title="reminder",
            content="reminder",
            user_id=sample_db_reminder.user_id,
            remind_date=datetime.datetime.now() + datetime.timedelta(days=1),
            delivery_method_ids=[
                sample_db_delivery_method_email.id,
            ],
        )
    res = await reminder_service.get_reminders_by_user_id(sample_db_reminder.user_id)
    assert res is not None
    assert len(res) == 4


@pytest.mark.asyncio
async def test_user_not_exists_get_by_user_id(reminder_service: ReminderService):
    res = await reminder_service.get_reminders_by_user_id(uuid4())
    assert res == []


@pytest.mark.asyncio
async def test_valid_delete(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.delete_reminder(
        sample_db_reminder.id, sample_db_reminder.user_id
    )
    assert res is not None
    assert await reminder_service.get_reminder(sample_db_reminder.id) is None


@pytest.mark.asyncio
async def test_not_exist_delete(reminder_service: ReminderService):
    res = await reminder_service.delete_reminder(uuid4(), uuid4())
    assert res is None


@pytest.mark.asyncio
async def test_valid_edit(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=3))
        )
        + datetime.timedelta(days=1),
    )
    edited = await reminder_service.edit_reminder(
        sample_db_reminder.id, data=new_data, user_id=sample_db_reminder.user_id
    )
    res = await reminder_service.get_reminder(sample_db_reminder.id)
    assert sample_db_reminder.edited_at is None
    assert res == edited
    assert res is not None
    assert res.title == new_data.title
    assert res.content == new_data.content
    assert res.remind_date == new_data.remind_date
    assert res.edited_at is not None
