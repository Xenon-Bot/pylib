from .checks import *
import types

__all__ = (
    "make_modal",
    "PartialModal"
)

def make_modal(cb, **kwargs):
    checks = []
    cooldown = None
    while isinstance(cb, Check):
        checks.append(cb)
        if isinstance(cb, Cooldown):
            cooldown = cb

        cb = cb.next

    values = {
        "callable": cb,
        "name": cb.__name__,
        "checks": checks,
        "cooldown": cooldown
    }

    values.update(kwargs)
    modal = PartialModal(**values)

    if cooldown is not None:
        cooldown.modal = modal

    return modal


class PartialModal:
    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.callable = kwargs["callable"]
        self.checks = kwargs.get("checks", [])
        self.cooldown = kwargs.get("cooldown")

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)
