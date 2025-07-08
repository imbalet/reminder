import asyncio

import aio_pika

from src.config import config
from src.services import SenderInterface, TelegramSender
from src.schemas import Message, Reminder, DeliveryMethodEnum

senders: dict[DeliveryMethodEnum, SenderInterface] = {
    DeliveryMethodEnum.TELEGRAM: TelegramSender(config.TG_BOT_TOKEN),
}


async def process_rmq_message(rmq_message: aio_pika.abc.AbstractIncomingMessage):
    decoded_message = rmq_message.body.decode()
    reminder = Reminder.model_validate_json(decoded_message)
    message = Message(title=reminder.title, content=reminder.content)

    async with rmq_message.process():
        for request in reminder.delivery_methods:
            sender = senders.get(request.delivery_method, None)
            if sender:
                res = await sender.send(  # noqa
                    contact_value=request.contact_value, message=message
                )
            else:
                # TODO: implement handling error
                pass


async def main():
    connection = await aio_pika.connect_robust(config.RMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(
        config.RMQ_ROUTING_KEY,
        durable=True,
    )

    await queue.consume(process_rmq_message)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
