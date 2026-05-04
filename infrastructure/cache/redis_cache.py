import json
from typing import Optional

from redis.asyncio import Redis

from core.ports import CacheProvider


class RedisCache(CacheProvider):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[dict]:
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: dict, ttl: int = 30) -> None:
        await self.redis.set(key, json.dumps(value), ex=ttl)
