import datetime
from uuid import uuid4

from aio_pika.pool import Pool
import pytest

from src.services import ReminderService, EventService
from src.schemas import ReminderResponse
from tests.config import config


async def create_reminder(
    reminder_service: ReminderService, remind_date: datetime.datetime | None, methods
):
    res = await reminder_service.create_reminder(
        title="reminder",
        content="reminder",
        user_id=uuid4(),
        remind_date=remind_date
        or datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=2),
        delivery_methods=methods,
    )
    return ReminderResponse.model_validate(res, from_attributes=True)


@pytest.mark.asyncio
async def test_sending_with_rabbitmq(
    reminder_service: ReminderService,
    send_service: EventService,
    rmq_channel_pool: Pool,
    sample_methods_data,
):
    async with rmq_channel_pool.acquire() as channel:
        queue = await channel.declare_queue(config.TEST_RMQ_ROUTING_KEY)
        await queue.purge()
        try:
            reminders = [
                await create_reminder(
                    reminder_service,
                    datetime.datetime.now(datetime.UTC),
                    sample_methods_data,
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
