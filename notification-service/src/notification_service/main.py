import asyncio
import logging

import aio_pika

from notification_service.config import config
from notification_service.services import SenderInterface, TelegramSender
from notification_service.schemas import Message, Reminder, DeliveryMethodEnum, ResultStatusEnum
from notification_service.logger import setup_logger
from rmq_service import ConsumeService, QueueConfig, ExchangeConfig

setup_logger()
logger = logging.getLogger(__name__)

senders: dict[DeliveryMethodEnum, SenderInterface] = {
    DeliveryMethodEnum.TELEGRAM: TelegramSender(config.TG_BOT_TOKEN),
}


async def process_rmq_message(message: aio_pika.abc.AbstractIncomingMessage):
    try:
        decoded_message = message.body.decode()
        reminder = Reminder.model_validate_json(decoded_message)
        notification_message = Message(title=reminder.title, content=reminder.content)

        for request in reminder.delivery_methods:
            sender = senders.get(request.delivery_method, None)
            method_type = request.delivery_method.value

            if not sender:
                logger.error(
                    "Unknown delivery method",
                    extra={
                        "method_type": method_type,
                        "operation": "send_reminder",
                        "result": "error",
                    },
                )
                raise Exception()

            try:
                res = await sender.send(
                    contact_value=request.contact_value, message=notification_message
                )
                if res.status == ResultStatusEnum.ERROR:
                    logger.warning(
                        "Failed to send reminder",
                        extra={
                            "method_type": method_type,
                            "operation": "send_reminder",
                            "data": res.data,
                            "result": "error",
                        },
                    )
                    raise Exception()
                else:
                    logger.info(
                        "Sent reminder",
                        extra={
                            "method_type": method_type,
                            "operation": "send_reminder",
                            "result": "success",
                        },
                    )
            except Exception as e:
                logger.exception(
                    "Unexpected error during sending",
                    extra={
                        "method_type": method_type,
                        "operation": "send_reminder",
                        "result": "error",
                        "error": str(e),
                    },
                )
                raise

    except Exception as e:
        logger.exception(
            "Message processing failed",
            extra={
                "operation": "process_message",
                "result": "error",
                "error": str(e),
            },
        )
        raise


def get_channel_pool():
    async def create_connection():
        return await aio_pika.connect_robust(config.RMQ_URL)

    async def create_channel():
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    connection_pool = aio_pika.pool.Pool(create_connection, max_size=10)
    channel_pool = aio_pika.pool.Pool(create_channel, max_size=100)
    return channel_pool


async def main():
    channel_pool = get_channel_pool()
    consume_service = ConsumeService(
        channel_pool=channel_pool,
        queue_config=QueueConfig(name=config.RMQ_REMINDERS_QUEUE),
        dlq=QueueConfig(name=config.RMQ_DLQ_FAILED_REMINDERS_NAME),
        dlx=ExchangeConfig(
            name=config.RMQ_DLX_FAILED_REMINDERS_NAME, type=aio_pika.ExchangeType.FANOUT
        ),
    )
    await consume_service.setup()

    asyncio.create_task(consume_service.consume(callback=process_rmq_message))

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
