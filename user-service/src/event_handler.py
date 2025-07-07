import aio_pika

from src.schemas import User
from src.services import UserService


async def consume(url: str, queue_name: str, session_factory):
    connection = await aio_pika.connect_robust(url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue(
        queue_name,
        durable=False,
    )

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                message_data = message.body.decode()
                user = User.model_validate_json(message_data)
                service = UserService(session_factory)
                await service.add(user_id=user.id, name=user.name, email=user.email)
