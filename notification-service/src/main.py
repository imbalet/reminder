import asyncio
import aio_pika
from src.config import config


async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        print(message.body.decode())


async def main():
    connection = await aio_pika.connect_robust(config.RMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(
        config.RMQ_ROUTING_KEY,
        durable=True,
    )

    await queue.consume(process_message)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
