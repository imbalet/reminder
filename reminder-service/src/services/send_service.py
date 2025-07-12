from datetime import datetime, timezone

import aio_pika
from sqlalchemy import update, and_
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.schemas import ReminderResponse
from src.models import RemindersOrm, Status
from src.config import config


class SendService:

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        channel_pool: aio_pika.pool.Pool[aio_pika.channel.Channel],
        routing_key=config.RMQ_ROUTING_KEY,
    ) -> None:
        self.session_factory = session_factory
        self.channel_pool = channel_pool
        self.routing_key = routing_key

    async def get_upcoming_reminders(self) -> list[ReminderResponse]:
        async with self.session_factory() as session:
            stmt = (
                update(RemindersOrm)
                .filter(
                    and_(
                        RemindersOrm.status == Status.PENDING,
                        RemindersOrm.remind_date <= datetime.now(timezone.utc),
                    )
                )
                .values(status=Status.SENT)
                .returning(RemindersOrm)
            )
            result = await session.execute(stmt)
            res = result.scalars().all()
            await session.commit()
            return [
                ReminderResponse.model_validate(rem, from_attributes=True)
                for rem in res
            ]

    async def send_reminders(self, reminders: list[ReminderResponse]):
        async with self.channel_pool.acquire() as channel:
            for reminder in reminders:
                message = aio_pika.Message(
                    body=reminder.model_dump_json().encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json",
                    content_encoding="utf-8",
                )
                await channel.default_exchange.publish(
                    message,
                    routing_key=self.routing_key,
                    timeout=5,
                )
