import datetime
import os
from uuid import uuid4

from aio_pika.pool import Pool
import pytest

from src.services import ReminderService, SendService
from src.schemas import ReminderResponse


async def create_reminder(
    reminder_service: ReminderService, remind_date: datetime.datetime | None
):
    res = await reminder_service.create_reminder(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=remind_date
        or datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=2),
    )
    return ReminderResponse.model_validate(res, from_attributes=True)


@pytest.mark.asyncio
async def test_get_upcoming_valid(
    reminder_service: ReminderService, send_service: SendService
):
    _ = [
        await create_reminder(
            reminder_service,
            datetime.datetime.now(datetime.UTC),
        )
        for _ in range(10)
    ]
    res = await send_service.get_upcoming_reminders()
    assert len(res) == 10
    res = await send_service.get_upcoming_reminders()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_sending_with_rabbitmq(
    reminder_service: ReminderService, send_service: SendService, channel_pool: Pool
):
    ROUTING_KEY = os.getenv("TEST_RMQ_ROUTING_KEY")
    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(ROUTING_KEY)
        await queue.purge()
        try:

            reminders = [
                await create_reminder(
                    reminder_service, datetime.datetime.now(datetime.UTC)
                )
                for _ in range(10)
            ]
            await send_service.send_reminders(reminders)

            messages = []
            for _ in range(10):
                message = await queue.get(timeout=3.0)
                async with message.process():
                    model = ReminderResponse.model_validate_json(message.body.decode())
                    messages.append(model)
                    message.ack()

            assert len(messages) == 10

        finally:
            await queue.purge()
