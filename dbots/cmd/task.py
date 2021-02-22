from datetime import timedelta
import asyncio
import traceback
import types


__all__ = (
    "Task",
)


class Task:
    def __init__(self, _callable, **td):
        self.callable = _callable
        self.td = timedelta(**td)

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)

    async def run(self):
        while True:
            await asyncio.sleep(self.td.total_seconds())
            try:
                await self.callable()
            except asyncio.CancelledError:
                raise
            except:
                traceback.print_exc()
