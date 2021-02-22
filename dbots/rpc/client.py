import json
import asyncio
from aioredis.pubsub import Receiver
import traceback
import uuid
import weakref


__all__ = (
    "RPCClient",
)


class RPCClient:
    def __init__(self, redis, bucket="default", loop=None):
        self._redis = redis
        self.loop = loop or asyncio.get_event_loop()
        self._mpsc = Receiver()
        self.bucket = bucket

        self._listeners = {}
        self._waiting = weakref.WeakValueDictionary()

    def get_call_key(self, name):
        return f"rpc:call:{self.bucket}:{name}"

    def get_response_key(self, call_id):
        return f"rpc:resp:{self.bucket}:{call_id}"

    async def _execute(self, payload, all=False):
        response_key = self.get_response_key(payload["id"])
        listeners = self._listeners.get(payload["name"], set())
        if len(listeners) == 0:
            return

        async def _exectutor(listener):
            result = await listener(*payload["args"], **payload["kwargs"])
            await self._redis.publish(response_key, json.dumps({
                "id": payload["id"],
                "response": result
            }))

        if all:
            await asyncio.gather([_exectutor(l) for l in listeners], return_exceptions=True)

        else:
            await _exectutor(listeners[0])

    async def run_reader(self, *events):
        await self._redis.subscribe(*[
            self._mpsc.pattern(self.get_call_key(e))
            for e in events
        ], self._mpsc.pattern(self.get_response_key("*")))

        async for _, msg in self._mpsc.iter():
            try:
                payload = json.loads(msg)
                if "response" in payload:
                    if payload["id"] in self._waiting:
                        fut = self._waiting[payload["id"]]
                        if not fut.done():
                            fut.set_result(payload["response"])

                    continue

                all = True
                if "compete" in payload:
                    all = False
                    payload = await self._redis.get(payload["compete"])
                    if payload is None:
                        # Someone else has already processed this
                        continue

                self.loop.create_task(self._execute(payload, all=all))
            except:
                traceback.print_exc()

    async def wait_for(self, name, timeout=5.0):
        future = asyncio.Future()
        if name in self._listeners:
            self._listeners[name].add(future)

        else:
            self._listeners[name] = {future}

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            try:
                self._listeners[name].remove(future)
            except KeyError:
                pass

    async def _wait_for_response(self, call_id, timeout=5.0):
        future = asyncio.Future()
        self._waiting[call_id] = future
        return asyncio.wait_for(future, timeout=timeout)

    async def call(self, name, timeout=5.0, *args, **kwargs):
        call_id = uuid.uuid4().hex
        payload = {
            "id": call_id,
            "name": name,
            "args": list(args),
            "kwargs": dict(kwargs)
        }
        await self._redis.setex(call_id, timeout, json.dumps(payload))
        await self._redis.publish(self.get_call_key(name), json.dumps({"compete": call_id}))
        return await self._wait_for_response(call_id, timeout)

    async def call_all(self, name, timeout=5.0, *args, **kwargs):
        call_id = uuid.uuid4().hex
        payload = {
            "id": call_id,
            "name": name,
            "args": list(args),
            "kwargs": dict(kwargs)
        }
        await self._redis.publish(self.get_call_key(name), json.dumps(payload))
        while True:
            yield await self._wait_for_response(call_id, timeout=timeout)

    def provide(self, name, callable=None):
        if name not in self._listeners:
            self._listeners[name] = set()

        if callable is None:
            def predicate(callable):
                self._listeners[name].add(callable)

            return predicate

        else:
            self._listeners[name].add(callable)
