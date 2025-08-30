import asyncio
import logging

from confirm_service.services import TelegramService
from confirm_service.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


async def main():
    logger.info("Launching app ...")
    service = TelegramService()
    task = service.start_bot()
    logger.info("Telegram bot started")
    await task


if __name__ == "__main__":
    asyncio.run(main())
