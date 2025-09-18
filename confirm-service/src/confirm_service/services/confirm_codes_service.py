from redis import asyncio as aioredis
import random


class ConfirmCodesService:
    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis

    @staticmethod
    def _generate_code(n: int = 6) -> str:
        code = random.randrange(0, 10**n)
        return f"{code:06d}"

    async def create_code(self, chat_id: str) -> str | None:
        for retries in range(10):
            code = self._generate_code()
            result = await self.redis.set(
                f"tg_confirm_code:{code}", chat_id, ex=300, nx=True
            )
            if result:
                return code
        return None
