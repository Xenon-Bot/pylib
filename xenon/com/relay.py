import asyncio
import aioredis
import weakref
import uuid
import orjson
import inspect

__all__ = (
    "Relay",
)


class Relay:
    def __init__(self, redis, **kwargs):
        self.redis = redis
        self.loop = kwargs.get("loop", asyncio.get_event_loop())

        self._mpsc = aioredis.pubsub.Receiver()
        self._reader_task = None

        self._subscribers = weakref.WeakSet()

    async def _reader(self):
        try:
            async for channel, msg in self._mpsc.iter():
                for fut in self._subscribers:
                    if not fut.done():
                        fut.set_result((channel, msg))

                self._subscribers.clear()
        finally:
            self._reader_task = None

    async def _iter(self):
        while self._mpsc.is_active:
            fut = asyncio.Future()
            self._subscribers.add(fut)
            yield await fut

    def start_reader(self):
        if self._reader_task is None:
            self._reader_task = self.loop.create_task(self._reader())

    async def subscribe(self, *channels, pattern=False):
        channel_factory = self._mpsc.channel if not pattern else self._mpsc.pattern
        await self.redis.subscribe(*[channel_factory(c) for c in channels])
        self.start_reader()
        async for channel, msg in self._iter():
            if channel.name.decode("utf-8") in channels:
                yield channel, msg

    async def unsubscribe(self, *channels, pattern=False):
        channel_factory = self._mpsc.channel if not pattern else self._mpsc.pattern
        await self.redis.unsubscribe(*[channel_factory(c) for c in channels])

    async def publish(self, channel, data):
        await self.redis.publish(channel, data)

    async def subscribe_compete(self, *channels, pattern=False):
        channel_factory = self._mpsc.channel if not pattern else self._mpsc.pattern
        await self.redis.subscribe(*[channel_factory(c) for c in channels])
        self.start_reader()
        async for channel, msg in self._iter():
            channel_name = channel.name.decode("utf-8")
            compete_key = msg.decode("utf-8")
            if channel_name in channels:
                data = await self.redis.get(f"compete:{compete_key}")
                if data is not None:
                    yield channel, data

    async def publish_compete(self, channel: str, data: str):
        compete_key = str(uuid.uuid4())
        await self.redis.setex(f"compete:{compete_key}", 10, data)
        await self.redis.publish(channel, compete_key)

    async def provide_rpc(self, name, _callable):
        async for _, msg in self.subscribe_compete(f"rpc:{name}"):
            data = orjson.loads(msg)
            nonce = data["nonce"]
            args = data["args"]

            res = await _callable(*args)
            if inspect.isawaitable(res):
                res = await res

            if isinstance(res, tuple):
                res = list(res)

            else:
                res = [res]

            await self.publish(f"rpc:{nonce}", orjson.dumps(res))

    async def call_rpc(self, name, *args):
        nonce = str(uuid.uuid4())
        data = orjson.dumps({"nonce": nonce, "args": list(args)})
        await self.publish_compete(f"rpc:{name}", data)
        try:
            async for _, msg in self.subscribe(f"rpc:{nonce}"):
                res = orjson.loads(msg)
                if len(res) == 1:
                    return res[0]

                else:
                    return tuple(res)
        finally:
            await self.unsubscribe(f"rpc:{nonce}")

    async def provide_service(self, service):
        tasks = []

        for rpc in service.rpc_list:
            tasks.append(self.loop.create_task(self.provide_rpc(
                f"{service.name}:{rpc.name}",
                rpc.callable
            )))

        if len(tasks) > 0:
            return await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
