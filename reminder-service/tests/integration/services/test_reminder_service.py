import datetime
import zoneinfo
from uuid import uuid4

import pytest

from reminder_service.schemas import ReminderEdit, ReminderResponse, Status
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
    created = await reminder_service.create(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=datetime.datetime.now() + datetime.timedelta(days=1),
        delivery_method_ids=[
            sample_db_delivery_method_telegram.id,
            sample_db_delivery_method_email.id,
        ],
    )
    assert await reminder_service.get(created.id) is not None


@pytest.mark.asyncio
async def test_valid_creating_not_utc(
    reminder_service: ReminderService, sample_db_delivery_method_email
):
    time = datetime.datetime.now(
        zoneinfo.ZoneInfo("Europe/Moscow")
    ) + datetime.timedelta(days=1)
    created = await reminder_service.create(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=time,
        delivery_method_ids=[
            sample_db_delivery_method_email.id,
        ],
    )
    res = await reminder_service.get(created.id)
    assert res is not None
    assert res.remind_date == time


@pytest.mark.asyncio
async def test_valid_get(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.get(sample_db_reminder.id)
    assert res is not None
    assert res == sample_db_reminder


@pytest.mark.asyncio
async def test_not_exists_get(reminder_service: ReminderService):
    res = await reminder_service.get(uuid4())
    assert res is None


@pytest.mark.asyncio
async def test_valid_get_by_user_id(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.get_all(
        sample_db_reminder.user_id, page_size=100, page=1
    )
    assert res.items == [sample_db_reminder]


@pytest.mark.asyncio
async def test_valid_get_by_user_id_multiply(
    reminder_service: ReminderService,
    sample_db_reminder: ReminderResponse,
    sample_db_delivery_method_email,
):
    for _ in range(3):
        await reminder_service.create(
            title="reminder",
            content="reminder",
            user_id=sample_db_reminder.user_id,
            remind_date=datetime.datetime.now() + datetime.timedelta(days=1),
            delivery_method_ids=[
                sample_db_delivery_method_email.id,
            ],
        )
    res = await reminder_service.get_all(
        sample_db_reminder.user_id, page_size=100, page=1
    )
    assert res is not None
    assert len(res.items) == 4


@pytest.mark.asyncio
async def test_user_not_exists_get_by_user_id(reminder_service: ReminderService):
    res = await reminder_service.get_all(uuid4(), page_size=100, page=1)
    assert len(res.items) == 0


@pytest.mark.asyncio
async def test_valid_delete(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.delete(
        sample_db_reminder.id, sample_db_reminder.user_id
    )
    assert res is not None
    assert await reminder_service.get(sample_db_reminder.id) is None


@pytest.mark.asyncio
async def test_not_exist_delete(reminder_service: ReminderService):
    res = await reminder_service.delete(uuid4(), uuid4())
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
    edited = await reminder_service.edit(
        sample_db_reminder.id, data=new_data, user_id=sample_db_reminder.user_id
    )
    res = await reminder_service.get(sample_db_reminder.id)
    assert sample_db_reminder.edited_at is None
    assert res == edited
    assert res is not None
    assert res.title == new_data.title
    assert res.content == new_data.content
    assert res.remind_date == new_data.remind_date
    assert res.edited_at is not None


async def test_valid_deactivate_orphans(reminder_service: ReminderService):
    orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=uuid4(),
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[],
    )

    res = await reminder_service.deactivate_orphan_reminders(orphan.user_id)

    assert len(res) == 1
    assert res[0].id == orphan.id
    assert res[0].status == Status.INACTIVE


async def test_valid_deactivate_orphans_empty(reminder_service: ReminderService):
    res = await reminder_service.deactivate_orphan_reminders(uuid4())

    assert len(res) == 0


async def test_valid_deactivate_orphans_with_inactive_status(
    reminder_service: ReminderService,
):
    user_id = uuid4()
    orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[],
    )
    inactive = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[],
    )
    inactive = await reminder_service.set_status(inactive.id, Status.INACTIVE)

    all_reminders = await reminder_service.get_all(
        user_id=user_id, page=1, page_size=100
    )
    orphans = await reminder_service.deactivate_orphan_reminders(orphan.user_id)

    assert len(all_reminders.items) == 2
    assert all_reminders.items == [inactive, orphan]

    assert len(orphans) == 1
    assert orphans[0].id == orphan.id
    assert orphans[0].status == Status.INACTIVE


async def test_valid_deactivate_orphans_with_not_orphan(
    reminder_service: ReminderService, sample_db_delivery_method_telegram
):
    user_id = uuid4()
    orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[],
    )
    not_orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )

    all_reminders = await reminder_service.get_all(
        user_id=user_id, page=1, page_size=100
    )
    orphans = await reminder_service.deactivate_orphan_reminders(orphan.user_id)

    assert len(all_reminders.items) == 2
    assert all_reminders.items == [not_orphan, orphan]

    assert len(orphans) == 1
    assert orphans[0].id == orphan.id
    assert orphans[0].status == Status.INACTIVE


async def test_valid_deactivate_orphans_two_orphans(reminder_service: ReminderService):
    user_id = uuid4()
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[],
    )
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[],
    )

    orphans = await reminder_service.deactivate_orphan_reminders(user_id)

    assert len(orphans) == 2
    assert orphans[0].status == Status.INACTIVE
    assert orphans[1].status == Status.INACTIVE


async def test_deactivate_reminders_by_method(
    reminder_service: ReminderService, sample_db_delivery_method_telegram
):
    method = await reminder_service.create(
        title="title",
        content="content",
        user_id=uuid4(),
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )

    res = await reminder_service.deactivate_reminders_by_method(
        sample_db_delivery_method_telegram.id
    )

    assert len(res) == 1
    assert res[0].id == method.id
    assert res[0].status == Status.INACTIVE


async def test_deactivate_reminders_by_method_empty(reminder_service: ReminderService):
    res = await reminder_service.deactivate_reminders_by_method(uuid4())

    assert len(res) == 0


async def test_deactivate_reminders_by_method_with_inactive_status(
    reminder_service: ReminderService, sample_db_delivery_method_telegram
):
    user_id = uuid4()
    active = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )
    inactive = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[],
    )
    inactive = await reminder_service.set_status(inactive.id, Status.INACTIVE)

    all_reminders = await reminder_service.get_all(
        user_id=user_id, page=1, page_size=100
    )
    deactivated = await reminder_service.deactivate_reminders_by_method(
        sample_db_delivery_method_telegram.id
    )

    assert len(all_reminders.items) == 2
    assert all_reminders.items == [inactive, active]

    assert len(deactivated) == 1
    assert deactivated[0].id == active.id
    assert deactivated[0].status == Status.INACTIVE


async def test_deactivate_reminders_by_method_with_other_method(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram,
    sample_db_delivery_method_email,
):
    user_id = uuid4()
    reminder1 = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[sample_db_delivery_method_email.id],
    )
    reminder2 = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )

    all_reminders = await reminder_service.get_all(
        user_id=user_id, page=1, page_size=100
    )
    deactivated = await reminder_service.deactivate_reminders_by_method(
        sample_db_delivery_method_email.id
    )

    assert len(all_reminders.items) == 2
    assert all_reminders.items == [reminder2, reminder1]

    assert len(deactivated) == 1
    assert deactivated[0].id == reminder1.id
    assert deactivated[0].status == Status.INACTIVE


async def test_deactivate_reminders_by_method_two_methods(
    reminder_service: ReminderService, sample_db_delivery_method_telegram
):
    user_id = uuid4()
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.datetime.now(datetime.UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )

    orphans = await reminder_service.deactivate_reminders_by_method(
        sample_db_delivery_method_telegram.id
    )

    assert len(orphans) == 2
    assert orphans[0].status == Status.INACTIVE
    assert orphans[1].status == Status.INACTIVE
