import asyncio
import logging
import signal

import aio_pika
from rmq_service import ConsumeService, ExchangeConfig, QueueConfig
from send_service.config import config
from send_service.logger import setup_logger
from send_service.schemas import (
    DeliveryMethodEnum,
    Message,
    Reminder,
    ResultStatusEnum,
)
from send_service.services import SenderInterface, TelegramSender

setup_logger()
logger = logging.getLogger(__name__)

senders: dict[DeliveryMethodEnum, SenderInterface] = {
    DeliveryMethodEnum.TELEGRAM: TelegramSender(config.TG_BOT_TOKEN),
}


async def process_rmq_message(message: aio_pika.abc.AbstractIncomingMessage, **kwargs):
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
                    exc_info=True,
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
            exc_info=True,
        )
        raise


def get_channel_pools():
    async def create_connection():
        return await aio_pika.connect_robust(config.RMQ_URL)

    connection_pool = aio_pika.pool.Pool(create_connection, max_size=10)

    async def create_channel():
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool = aio_pika.pool.Pool(create_channel, max_size=100)
    return connection_pool, channel_pool


async def main():
    connection_pool, channel_pool = get_channel_pools()
    consume_service = ConsumeService(
        channel_pool=channel_pool,
        queue_config=QueueConfig(name=config.RMQ_REMINDERS_QUEUE),
        dlx=ExchangeConfig(
            name=config.RMQ_DLX_FAILED_REMINDERS_NAME, type=aio_pika.ExchangeType.FANOUT
        ),
    )
    await consume_service.setup()

    consume_task = asyncio.create_task(
        consume_service.consume(callback=process_rmq_message)
    )

    stop_event = asyncio.Event()

    logger.info("Send service started")

    def _signal_handler():
        logger.info("Shutdown signal received")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    await stop_event.wait()

    consume_task.cancel()
    try:
        await consume_task
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled")
    except NotImplementedError:
        logger.warning("Signal handlers are not supported on this platform")

    await channel_pool.close()
    await connection_pool.close()

    logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
