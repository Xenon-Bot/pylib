import types


__all__ = (
    "Service",
    "ExternalService"
)


class Service:
    relay = None
    name: str

    @property
    def rpc_list(self):
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Service.rpc):
                attr.callable = types.MethodType(attr.callable, self)
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


class ExternalService:
    def __init__(self, relay, name):
        self.relay = relay
        self.name = name

    def __getattr__(self, item):
        pass
