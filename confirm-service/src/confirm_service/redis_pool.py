from redis import asyncio as aioredis

from confirm_service.config import config

redis = aioredis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    db=0,
    max_connections=20,
)
