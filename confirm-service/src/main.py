import asyncio

from src.services import TelegramService


async def main():
    service = TelegramService()
    service.start_bot()

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
