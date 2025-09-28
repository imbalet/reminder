import asyncio
import logging

from confirm_service.logger import setup_logger
from confirm_service.redis_pool import redis
from confirm_service.services import TelegramService

setup_logger()
logger = logging.getLogger(__name__)


async def on_shutdown():
    logger.info("Shutdown callback triggered")
    await redis.aclose()
    await redis.connection_pool.disconnect()


async def main():
    logger.info("Launching app ...")
    service = TelegramService()
    bot_task = service.start_bot()

    logger.info("Telegram bot started")
    try:
        await bot_task
    finally:
        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
