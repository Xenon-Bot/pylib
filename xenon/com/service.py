from .relay import Relay


__all__ = (
    "Service",
)


class Service:
    relay: Relay
    name: str

    @property
    def rpc_list(self):
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Service.rpc):
                yield attr

    class rpc:
        def __init__(self, name_or_callable):
            self.name = None
            self.callable = None

            if isinstance(name_or_callable, str):
                self.name = name_or_callable

            else:
                self.callable = name_or_callable
                self.name = name_or_callable.__name__

        def __call__(self, callable):
            self.callable = callable
