import asyncio
import aioredis
import weakref
import uuid
import orjson

__all__ = (
    "Relay",
)


class RPCResult:
    def __init__(self, error, value):
        self.error = error

        if len(value) == 1:
            self.value = value[0]

        else:
            self.value = tuple(value)


class Relay:
    def __init__(self, redis, **kwargs):
        self.redis = redis
        self._loop = kwargs.get("loop")

        self._mpsc = aioredis.pubsub.Receiver()
        self._reader_task = None

        self._subscribers = weakref.WeakSet()

    @property
    def loop(self):
        return self._loop or asyncio.get_event_loop()

    async def _reader(self):
        try:
            async for _, msg in self._mpsc.iter():
                payload = orjson.loads(msg)
                event, data = payload["t"], payload["d"]
                for fut, check in self._subscribers:
                    if check(event, data) and not fut.done():
                        fut.set_result((event, data))
        finally:
            self._reader_task = None

    async def start_reader(self):
        if self._reader_task is None:
            await self.redis.psubscribe(self._mpsc.channel("rpc"))
            self._reader_task = self.loop.create_task(self._reader())

    async def subscribe(self, *events):
        await self.start_reader()
        while True:
            fut = self.loop.create_future()
            check = lambda e, d: e in events
            self._subscribers.add((fut, check))
            yield await fut

    async def publish(self, event, data):
        await self.redis.publish("rpc", orjson.dumps({
            "t": event,
            "d": data
        }))

    async def subscribe_compete(self, *events):
        async for event, key in self.subscribe(*events):
            data = await self.redis.get(f"rpc:compete:{key}")
            if data is not None:
                yield event, data

    async def publish_compete(self, event, data):
        compete_key = str(uuid.uuid4())
        await self.redis.setex(f"rpc:compete:{compete_key}", 10, orjson.dumps(data))
        await self.redis.publish("rpc", {"t": event, "d": compete_key})

    async def wait_for(self, *events, check=None, timeout=None):
        def _check(e, d):
            if e not in events:
                return False

            if check is not None and not check(d):
                return False

            return True

        fut = self.loop.create_future()
        self._subscribers.add((fut, _check))
        return await asyncio.wait_for(fut, timeout=timeout)
