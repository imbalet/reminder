import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio.session import async_sessionmaker, AsyncSession
from src.services import ReminderService
from src.schemas import ReminderResponse, ReminerEdit
from src.exceptions import NotFoundError


@pytest.fixture
async def sample_reminder(
    async_session_factory: async_sessionmaker[AsyncSession],
    reminder_service: ReminderService,
):
    res = await reminder_service.create_reminder(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=datetime.datetime.now(),
    )
    return ReminderResponse.model_validate(res, from_attributes=True)


# ------------------------------------#
#               TESTS                 #
# ------------------------------------#


@pytest.mark.asyncio
async def test_valid_creating(reminder_service: ReminderService):
    created = await reminder_service.create_reminder(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=datetime.datetime.now(),
    )
    assert await reminder_service.get_reminder(created.id) is not None


@pytest.mark.asyncio
async def test_valid_get(
    reminder_service: ReminderService, sample_reminder: ReminderResponse
):
    res = await reminder_service.get_reminder(sample_reminder.id)
    assert res is not None
    assert res == sample_reminder


@pytest.mark.asyncio
async def test_not_exists_get(reminder_service: ReminderService):
    res = await reminder_service.get_reminder(uuid4())
    assert res is None


@pytest.mark.asyncio
async def test_valid_get_by_user_id(
    reminder_service: ReminderService, sample_reminder: ReminderResponse
):
    res = await reminder_service.get_reminders_by_user_id(sample_reminder.user_id)
    assert res is not None
    assert res[0] == sample_reminder


@pytest.mark.asyncio
async def test_valid_get_by_user_id_multiply(
    reminder_service: ReminderService, sample_reminder: ReminderResponse
):
    for _ in range(3):
        await reminder_service.create_reminder(
            title="reminder",
            content="reminder",
            user_id=sample_reminder.user_id,
            remind_date=datetime.datetime.now(),
        )
    res = await reminder_service.get_reminders_by_user_id(sample_reminder.user_id)
    assert res is not None
    assert len(res) == 4


@pytest.mark.asyncio
async def test_user_not_exists_get_by_user_id(reminder_service: ReminderService):
    res = await reminder_service.get_reminders_by_user_id(uuid4())
    assert res == []


@pytest.mark.asyncio
async def test_valid_delete(
    reminder_service: ReminderService, sample_reminder: ReminderResponse
):
    await reminder_service.delete_reminder(sample_reminder.id)
    assert await reminder_service.get_reminder(sample_reminder.id) is None


@pytest.mark.asyncio
async def test_not_exist_delete(reminder_service: ReminderService):
    with pytest.raises(NotFoundError):
        await reminder_service.delete_reminder(uuid4())


@pytest.mark.asyncio
async def test_valid_edit(
    reminder_service: ReminderService, sample_reminder: ReminderResponse
):
    new_data = ReminerEdit(
        title="new_title",
        content="new content",
        remind_date=datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=3))
        ),
    )
    edited = await reminder_service.edit_reminder(sample_reminder.id, data=new_data)
    res = await reminder_service.get_reminder(sample_reminder.id)
    assert res == edited
    assert res is not None
    assert res.title == new_data.title
    assert res.content == new_data.content
    assert res.remind_date == new_data.remind_date
    assert res.edited_at is not None
