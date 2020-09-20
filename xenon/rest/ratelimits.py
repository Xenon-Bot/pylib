from abc import ABC
import asyncio


__all__ = (
    "Ratelimit",
    "BaseRatelimitHandler",
    "RedisRatelimitHandler"
)


class Ratelimit:
    def __init__(self, delta, remaining=None, is_global=False):
        self.delta = delta
        self.remaining = remaining
        self.is_global = is_global

    async def wait(self):
        if self.remaining == 0:
            await asyncio.sleep(self.delta)


class BaseRatelimitHandler(ABC):
    def __init__(self, **kwargs):
        self.loop = kwargs.get("loop", asyncio.get_event_loop())

    async def get_global(self):
        pass

    async def set_global(self, delta: float):
        pass

    async def get_bucket(self, bucket: str):
        pass

    async def set_bucket(self, bucket: str, delta: float, remaining: int):
        pass


class RedisRatelimitHandler(BaseRatelimitHandler):
    def __init__(self, redis, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis

    async def get_global(self):
        delta = await self.redis.pttl("ratelimits:global")
        if delta < 0:
            return None

        return Ratelimit(delta / 1000, remaining=0, is_global=True)

    async def set_global(self, delta: float):
        await self.redis.setex("ratelimits:global", delta, 1)

    async def get_bucket(self, bucket):
        delta = await self.redis.pttl(f"ratelimits:{bucket}")
        if delta < 0:
            return None

        remaining = await self.redis.get(f"ratelimits:{bucket}")
        if remaining is None:
            return None

        return Ratelimit(delta / 1000, int(remaining))

    async def set_bucket(self, bucket: str, delta: float, remaining: int):
        await self.redis.setex(f"ratelimits:{bucket}", delta, remaining)
