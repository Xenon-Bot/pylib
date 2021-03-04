import types


__all__ = (
    "ToProvide",
    "Service"
)


class ToProvide:
    def __init__(self, _callable, name):
        self.name = name
        self.callable = _callable

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)


class Service:
    def __init__(self, client):
        self.client = client
        self.to_provide = []
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, ToProvide):
                attr.bind(self)
                self.to_provide.append(attr)

    @property
    def redis(self):
        return self.client.redis

    @staticmethod
    def provide(_callable=None, name=None):
        if _callable is None:
            def _predicate(_callable):
                _name = name or _callable.__name__
                return ToProvide(_callable, _name)

            return _predicate

        else:
            name = name or _callable.__name__
            return ToProvide(_callable, name)
