import types
import inspect

__all__ = (
    "Listener",
)


class Listener:
    def __init__(self, _callable, event):
        self.callable = _callable
        self.event = event

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)

    async def execute(self, data):
        res = self.callable(data)
        if inspect.isawaitable(res):
            return await res

        return res
