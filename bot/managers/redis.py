import os
import redis.asyncio as redis

class RedisManager:
    def __init__(self, url: str | None = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.url, encoding="utf-8", decode_responses=True)
    
    async def get(self, key: str) -> str | None:
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, expire_seconds: int | None = None) -> None:
        if expire_seconds:
            await self.client.set(key, value, ex=expire_seconds)
        else:
            await self.client.set(key, value)
    
    async def delete(self, key: str) -> None:
        await self.client.delete(key)