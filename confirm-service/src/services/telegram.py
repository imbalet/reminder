import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters.command import Command
from aiogram.types import Message

from src.config import config
from src.services import ConfirmCodesService
from redis_pool import redis


dp = Dispatcher()


@dp.message(Command("link"))
async def link_handler(message: Message) -> None:
    try:
        service = ConfirmCodesService(redis)
        code = await service.create_code(str(message.chat.id))
        if not code:
            await message.answer("Error creating code, try again later")
        else:
            await message.answer(
                f"Your confirm code:\n<code>{code}</code>", parse_mode="HTML"
            )
    except Exception:
        # logging here
        await message.answer("Unexpected error")


class TelegramService:
    def __init__(self):
        pass

    def start_bot(self):
        api_server = TelegramAPIServer.from_base(config.TG_API_ADDRESS, is_local=True)
        bot = Bot(
            token=config.TG_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            session=AiohttpSession(api=api_server),
        )
        asyncio.create_task(dp.start_polling(bot))
