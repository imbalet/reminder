import asyncio
import logging

from src.services import TelegramService
from src.logger import setup_logger

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
