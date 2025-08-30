import logging
from typing import Awaitable, Callable
import aio_pika

from reminder_service.schemas import ReminderResponse
from reminder_service.config import config

logger = logging.getLogger(__name__)


class SendService:

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


class EventService:
    def __init__(
        self,
        channel_pool: aio_pika.pool.Pool[aio_pika.channel.Channel],
        queue_name: str,
    ) -> None:
        self.channel_pool = channel_pool
        self.queue_name = queue_name

    async def consume(
        self,
        queue_name,
        sync_callback: Callable[..., None] | None = None,
        async_callback: Callable[..., Awaitable[None]] | None = None,
        *args,
        **kwargs
    ):
        if not (sync_callback or async_callback):
            raise ValueError("At least one callback must be provided")
        if sync_callback and async_callback:
            raise ValueError("Only one callback can be used")
        try:
            async with self.channel_pool.acquire() as channel:
                await channel.set_qos(prefetch_count=10)

                queue = await channel.declare_queue(
                    queue_name,
                    durable=True,
                )

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        try:
                            async with message.process():
                                message_data = message.body.decode()
                                if async_callback:
                                    await async_callback(message_data, *args, **kwargs)
                                else:
                                    sync_callback(message_data, *args, **kwargs)  # type: ignore

                        except Exception:
                            logger.error("Error processing message", exc_info=True)
        except Exception:
            logger.critical("Consume task stopped", exc_info=True)
