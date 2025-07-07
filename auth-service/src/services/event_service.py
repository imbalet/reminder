import aio_pika

from src.schemas import UserRmqData
from src.config import config

TIME_OFFSET_MINUTES = 1


class EventService:

    def __init__(
        self,
        channel_pool: aio_pika.pool.Pool[aio_pika.channel.Channel],
        routing_key=config.RMQ_EVENTS_QUEUE,
    ) -> None:
        self.channel_pool = channel_pool
        self.routing_key = routing_key

    async def send_registration_event(self, user: UserRmqData):
        async with self.channel_pool.acquire() as channel:
            message = aio_pika.Message(
                body=user.model_dump_json(exclude={"registered_at"}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
                content_encoding="utf-8",
            )
            await channel.default_exchange.publish(
                message,
                routing_key=self.routing_key,
                timeout=5,
            )
