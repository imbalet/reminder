import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters.command import Command
from aiogram.types import Message

from confirm_service.config import config
from confirm_service.services import ConfirmCodesService
from confirm_service.redis_pool import redis


logger = logging.getLogger(__name__)
dp = Dispatcher()


@dp.message(Command("link"))
async def link_handler(message: Message) -> None:
    try:
        service = ConfirmCodesService(redis)
        user_name = (
            message.from_user.username
            if message.from_user and message.from_user.username
            else "Unknown"
        )
        code = await service.create_code(
            str(message.chat.id),
            user_name,
        )
        if not code:
            logger.error(
                "Error creating confirm code",
                extra={
                    "method_type": "telegram",
                    "operation": "create_confirm_code",
                    "result": "error",
                },
            )
            await message.answer("Error creating code, try again later")
        else:
            logger.info(
                "Created confirm code",
                extra={
                    "method_type": "telegram",
                    "operation": "create_confirm_code",
                    "result": "success",
                },
            )
            await message.answer(
                f"Your confirm code:\n<code>{code}</code>", parse_mode="HTML"
            )
    except Exception:
        logger.error(
            "Unexpected error on creating confirm code",
            extra={
                "method_type": "telegram",
                "operation": "create_confirm_code",
                "result": "error",
            },
        )
        await message.answer("Unexpected error")


class TelegramService:
    def __init__(self):
        pass

    def start_bot(self):
        if config.TG_API_ADDRESS:
            api_server = TelegramAPIServer.from_base(
                config.TG_API_ADDRESS, is_local=True
            )
            session = AiohttpSession(api=api_server)
        else:
            session = None
        bot = Bot(
            token=config.TG_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            session=session,
        )
        return asyncio.create_task(dp.start_polling(bot))
