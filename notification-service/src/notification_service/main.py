import asyncio
import logging

import aio_pika

from notification_service.config import config
from notification_service.services import SenderInterface, TelegramSender
from notification_service.schemas import Message, Reminder, DeliveryMethodEnum, ResultStatusEnum
from notification_service.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

senders: dict[DeliveryMethodEnum, SenderInterface] = {
    DeliveryMethodEnum.TELEGRAM: TelegramSender(config.TG_BOT_TOKEN),
}


async def process_rmq_message(rmq_message: aio_pika.abc.AbstractIncomingMessage):
    processing_success = True

    try:
        decoded_message = rmq_message.body.decode()
        reminder = Reminder.model_validate_json(decoded_message)
        message = Message(title=reminder.title, content=reminder.content)

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
                processing_success = False
                continue

            try:
                res = await sender.send(
                    contact_value=request.contact_value, message=message
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
                    processing_success = False
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
                processing_success = False

    except Exception as e:
        logger.exception(
            "Message processing failed",
            extra={
                "operation": "process_message",
                "result": "error",
                "error": str(e),
            },
        )
        processing_success = False

    if processing_success:
        await rmq_message.ack()
    else:
        await rmq_message.nack(requeue=False)


async def main():
    connection = await aio_pika.connect_robust(config.RMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    await channel.declare_exchange(config.RMQ_DLX_NAME, durable=True)
    await channel.declare_queue(config.RMQ_DLQ_NAME, durable=True)
    reminder_queue = await channel.declare_queue(
        config.RMQ_ROUTING_KEY,
        durable=True,
        arguments={
            "x-dead-letter-exchange": config.RMQ_DLX_NAME,
            "x-dead-letter-routing-key": config.RMQ_DLQ_NAME,
        },
    )

    await reminder_queue.consume(process_rmq_message)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
