from .command import *
from .task import *
from .components import *


__all__ = (
    "Module",
)


class Module:
    def __init__(self, bot):
        self.bot = bot

        self.commands = []
        self.tasks = []
        self.buttons = []
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Command):
                attr.bind(self)
                self.commands.append(attr)

            elif isinstance(attr, Task):
                attr.bind(self)
                self.tasks.append(attr)

            elif isinstance(attr, PartialButton):
                attr.bind(self)
                self.buttons.append(attr)

    @staticmethod
    def command(_callable=None, **kwargs):
        if _callable is None:
            def _predicate(_callable):
                return make_command(Command, _callable, **kwargs)

            return _predicate

        return make_command(Command, _callable, **kwargs)

    @staticmethod
    def button(_callable=None, **kwargs):
        if _callable is None:
            def _predicate(_callable):
                return PartialButton(
                    name=kwargs.get("name", _callable.__name__),
                    callable=_callable
                )

            return _predicate

        return PartialButton(
            name=kwargs.get("name", _callable.__name__),
            callable=_callable
        )

    @staticmethod
    def task(**td):
        def _predicate(_callable):
            return Task(_callable, **td)

        return _predicate

    async def post_setup(self):
        pass
