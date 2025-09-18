import asyncio
import logging
import signal

from confirm_service.services import TelegramService
from confirm_service.logger import setup_logger
from confirm_service.redis_pool import redis

setup_logger()
logger = logging.getLogger(__name__)


async def main():
    logger.info("Launching app ...")
    service = TelegramService()
    task = service.start_bot()
    logger.info("Telegram bot started")

    stop_event = asyncio.Event()

    def _signal_handler():
        logger.info("Shutdown signal received")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            logger.warning("Signal handlers are not supported on this platform")

    await stop_event.wait()

    logger.info("Stopping bot...")
    task.cancel()
    await redis.close()
    await redis.connection_pool.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
