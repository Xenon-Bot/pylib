import types
from datetime import timedelta
import asyncio
import traceback

__all__ = (
    "Task",
)


class Task:
    def __init__(self, _callable, **td_kwargs):
        self.callable = _callable
        self._delta = timedelta(**td_kwargs)
        self._task = None

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)

    def start(self, loop):
        self._task = loop.create_task(self.run())

    def stop(self):
        if self._task is not None and not self._task.done():
            self._task.cancel()

    async def run(self):
        while True:
            await asyncio.sleep(self._delta.total_seconds())
            try:
                await self.callable()
            except:
                traceback.print_exc()
