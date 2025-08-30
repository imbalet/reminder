from typing import Awaitable, Callable
import logging

from aio_pika.pool import Pool
from aio_pika import Channel

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, channel_pool: Pool[Channel], queue_name: str):
        self.channel_pool = channel_pool
        self.queue_name = queue_name

    async def consume(
        self,
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
                    self.queue_name,
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
