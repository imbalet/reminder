import zoneinfo
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from reminder_service.schemas import ReminderEdit, ReminderResponse, Status
from reminder_service.schemas.delivery_methods import DeliveryMethod
from reminder_service.services import ReminderService
from reminder_service.services.delivery_method import DeliveryMethodService


async def test_create(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    sample_db_delivery_method_email: DeliveryMethod,
    user_id: UUID,
):
    created = await reminder_service.create(
        title="reminder",
        content="reminder",
        user_id=user_id,
        remind_date=datetime.now() + timedelta(days=1),
        delivery_method_ids=[
            sample_db_delivery_method_telegram.id,
            sample_db_delivery_method_email.id,
        ],
    )
    assert await reminder_service.get(created.id) is not None


async def test_create_not_utc(
    reminder_service: ReminderService,
    sample_db_delivery_method_email: DeliveryMethod,
    user_id: UUID,
):
    time = datetime.now(zoneinfo.ZoneInfo("Europe/Moscow")) + timedelta(days=1)
    created = await reminder_service.create(
        title="reminder",
        content="reminder",
        user_id=user_id,
        remind_date=time,
        delivery_method_ids=[
            sample_db_delivery_method_email.id,
        ],
    )
    res = await reminder_service.get(created.id)
    assert res is not None
    assert res.remind_date == time


async def test_create_with_invalid_delivery_method(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    sample_db_delivery_method_email: DeliveryMethod,
    user_id: UUID,
):

    with pytest.raises(ValueError):
        await reminder_service.create(
            title="reminder",
            content="reminder",
            user_id=user_id,
            remind_date=datetime.now() + timedelta(days=1),
            delivery_method_ids=[
                sample_db_delivery_method_telegram.id,
                sample_db_delivery_method_email.id,
                uuid4(),
            ],
        )


async def test_create_with_invalid_delivery_method_other_user(
    reminder_service: ReminderService,
    delivery_methods_service: DeliveryMethodService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    sample_db_delivery_method_email: DeliveryMethod,
    user_id: UUID,
):
    new_method = await delivery_methods_service.create(
        id=uuid4(),
        delivery_method=sample_db_delivery_method_telegram.delivery_method,
        contact_value=sample_db_delivery_method_telegram.contact_value,
        user_id=uuid4(),
        meta_data=sample_db_delivery_method_telegram.meta_data
    )

    with pytest.raises(ValueError):
        await reminder_service.create(
            title="reminder",
            content="reminder",
            user_id=user_id,
            remind_date=datetime.now() + timedelta(days=1),
            delivery_method_ids=[
                sample_db_delivery_method_telegram.id,
                sample_db_delivery_method_email.id,
                new_method.id,
            ],
        )


async def test_get(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.get(sample_db_reminder.id)
    assert res is not None
    assert res == sample_db_reminder


async def test_get_not_exists(reminder_service: ReminderService):
    res = await reminder_service.get(uuid4())
    assert res is None


async def test_get_by_user_id(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.get_all(
        sample_db_reminder.user_id, page_size=100, page=1
    )
    assert res.items == [sample_db_reminder]


async def test_get_by_user_id_multiply(
    reminder_service: ReminderService,
    sample_db_reminder: ReminderResponse,
    sample_db_delivery_method_email: DeliveryMethod,
):
    for _ in range(3):
        await reminder_service.create(
            title="reminder",
            content="reminder",
            user_id=sample_db_reminder.user_id,
            remind_date=datetime.now() + timedelta(days=1),
            delivery_method_ids=[
                sample_db_delivery_method_email.id,
            ],
        )
    res = await reminder_service.get_all(
        sample_db_reminder.user_id, page_size=100, page=1
    )
    assert res is not None
    assert len(res.items) == 4


async def test_get_by_user_id_user_not_exists(reminder_service: ReminderService):
    res = await reminder_service.get_all(uuid4(), page_size=100, page=1)
    assert len(res.items) == 0


async def test_delete(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    res = await reminder_service.delete(
        sample_db_reminder.id, sample_db_reminder.user_id
    )
    assert res is not None
    assert await reminder_service.get(sample_db_reminder.id) is None


async def test_delete_not_exist(reminder_service: ReminderService):
    res = await reminder_service.delete(uuid4(), uuid4())
    assert res is None


async def test_edit(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
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
    assert res.delivery_methods == sample_db_reminder.delivery_methods


async def test_edit_forbidden(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )
    edited = await reminder_service.edit(
        uuid4(), data=new_data, user_id=sample_db_reminder.user_id
    )

    assert edited is None


async def test_edit_forbidden_other_user(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    new_data = ReminderEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.now(UTC) + timedelta(days=1),
    )
    edited = await reminder_service.edit(
        sample_db_reminder.id, data=new_data, user_id=uuid4()
    )

    assert edited is None


async def test_edit_delivery_methods_add(
    reminder_service: ReminderService,
    delivery_methods_service: DeliveryMethodService,
    sample_db_reminder: ReminderResponse,
    sample_db_delivery_method_telegram: DeliveryMethod,
):
    new_method = await delivery_methods_service.create(
        id=uuid4(),
        delivery_method=sample_db_delivery_method_telegram.delivery_method,
        contact_value="123456",
        user_id=sample_db_reminder.user_id,
        meta_data=sample_db_delivery_method_telegram.meta_data,
    )
    new_data = ReminderEdit(
        delivery_methods_ids=[
            new_method.id,
            *[i.id for i in sample_db_reminder.delivery_methods],
        ]
    )
    edited = await reminder_service.edit(
        sample_db_reminder.id, data=new_data, user_id=sample_db_reminder.user_id
    )
    res = await reminder_service.get(sample_db_reminder.id)
    assert sample_db_reminder.edited_at is None
    assert res == edited
    assert res is not None and edited is not None
    assert res.edited_at is not None
    assert len(edited.delivery_methods) == 3


async def test_edit_delivery_methods_remove(
    reminder_service: ReminderService,
    sample_db_reminder: ReminderResponse,
    sample_db_delivery_method_telegram: DeliveryMethod,
):
    new_data = ReminderEdit(
        delivery_methods_ids=[sample_db_delivery_method_telegram.id]
    )
    edited = await reminder_service.edit(
        sample_db_reminder.id, data=new_data, user_id=sample_db_reminder.user_id
    )
    res = await reminder_service.get(sample_db_reminder.id)
    assert sample_db_reminder.edited_at is None
    assert res == edited
    assert res is not None and edited is not None
    assert res.edited_at is not None
    assert len(edited.delivery_methods) == 1


async def test_edit_delivery_methods_invalid_delivery_methods(
    reminder_service: ReminderService, sample_db_reminder: ReminderResponse
):
    new_data = ReminderEdit(delivery_methods_ids=[uuid4()])
    with pytest.raises(ValueError):
        await reminder_service.edit(
            sample_db_reminder.id, data=new_data, user_id=sample_db_reminder.user_id
        )


async def test_get_upcoming_reminders_one(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
):
    upcoming_reminder = await reminder_service.create(
        title="title",
        content="content",
        user_id=sample_db_delivery_method_telegram.user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )
    res = await reminder_service.get_upcoming_reminders()
    res2 = await reminder_service.get_upcoming_reminders()

    from_db = await reminder_service.get(upcoming_reminder.id)

    assert len(res) == 1
    assert len(res2) == 0
    assert res[0] == from_db
    assert from_db and from_db.status == Status.SENT


async def test_get_upcoming_reminders_10(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
):
    _ = [
        await reminder_service.create(
            title="title",
            content="content",
            user_id=sample_db_delivery_method_telegram.user_id,
            remind_date=datetime.now(UTC),
            delivery_method_ids=[sample_db_delivery_method_telegram.id],
        )
        for _ in range(10)
    ]
    res = await reminder_service.get_upcoming_reminders()

    res2 = await reminder_service.get_upcoming_reminders()

    assert len(res) == 10
    assert len(res2) == 0


async def test_get_upcoming_reminders_no_one(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
):
    await reminder_service.create(
        title="title",
        content="content",
        user_id=sample_db_delivery_method_telegram.user_id,
        remind_date=datetime.now(UTC) + timedelta(minutes=5),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )
    res = await reminder_service.get_upcoming_reminders()

    assert len(res) == 0


async def test_deactivate_orphans(reminder_service: ReminderService):
    orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=uuid4(),
        remind_date=datetime.now(UTC),
        delivery_method_ids=[],
    )

    res = await reminder_service.deactivate_orphan_reminders(orphan.user_id)

    assert len(res) == 1
    assert res[0].id == orphan.id
    assert res[0].status == Status.INACTIVE


async def test_deactivate_orphans_empty(reminder_service: ReminderService):
    res = await reminder_service.deactivate_orphan_reminders(uuid4())

    assert len(res) == 0


async def test_deactivate_orphans_with_inactive_status(
    reminder_service: ReminderService,
):
    user_id = uuid4()
    orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[],
    )
    inactive = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
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


async def test_deactivate_orphans_with_not_orphan(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    user_id: UUID,
):
    orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[],
    )
    not_orphan = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
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


async def test_deactivate_orphans_two_orphans(reminder_service: ReminderService):
    user_id = uuid4()
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[],
    )
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[],
    )

    orphans = await reminder_service.deactivate_orphan_reminders(user_id)

    assert len(orphans) == 2
    assert orphans[0].status == Status.INACTIVE
    assert orphans[1].status == Status.INACTIVE


async def test_deactivate_reminders_by_method(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    user_id: UUID,
):
    method = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
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
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    user_id: UUID,
):
    active = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )
    inactive = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
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
    sample_db_delivery_method_telegram: DeliveryMethod,
    sample_db_delivery_method_email: DeliveryMethod,
    user_id: UUID,
):
    reminder1 = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[sample_db_delivery_method_email.id],
    )
    reminder2 = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
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


async def test_deactivate_reminders_by_method_two_reminders(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    user_id: UUID,
):
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )
    await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[sample_db_delivery_method_telegram.id],
    )

    deactivated = await reminder_service.deactivate_reminders_by_method(
        sample_db_delivery_method_telegram.id
    )

    assert len(deactivated) == 2
    assert deactivated[0].status == Status.INACTIVE
    assert deactivated[1].status == Status.INACTIVE


async def test_deactivate_reminders_by_method_two_methods(
    reminder_service: ReminderService,
    sample_db_delivery_method_telegram: DeliveryMethod,
    sample_db_delivery_method_email: DeliveryMethod,
    user_id: UUID,
):
    rem = await reminder_service.create(
        title="title",
        content="content",
        user_id=user_id,
        remind_date=datetime.now(UTC),
        delivery_method_ids=[
            sample_db_delivery_method_telegram.id,
            sample_db_delivery_method_email.id,
        ],
    )

    deactivated = await reminder_service.deactivate_reminders_by_method(
        sample_db_delivery_method_telegram.id
    )

    rem_from_db = await reminder_service.get(rem.id)

    assert len(deactivated) == 0
    assert rem_from_db and rem_from_db.status == Status.PENDING
