from redis import asyncio as aioredis


class ConfirmCodesService:
    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis

    async def confirm(self, code: str) -> tuple[str, str] | None:
        """Return tuple [chat_id, username]"""
        key = f"tg_confirm_code:{code}"
        value = await self.redis.getdel(key)
        if value is None:
            return None

        return value.decode("utf-8").split(":", maxsplit=1)
