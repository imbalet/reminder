import aio_pika

from src.schemas import ReminderResponse
from src.config import config


class EventService:

    def __init__(
        self,
        channel_pool: aio_pika.pool.Pool[aio_pika.channel.Channel],
        routing_key=config.RMQ_ROUTING_KEY,
    ) -> None:
        self.channel_pool = channel_pool
        self.routing_key = routing_key

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
