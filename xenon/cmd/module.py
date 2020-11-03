__all__ = (
    "Module",
)


from .command import *
from .task import *


class Module:
    def __init__(self, bot):
        self.bot = bot

        self.commands = []
        self.tasks = []

        self._discover_objects()
        self.bot.loop.create_task(self.setup())

    def _discover_objects(self):
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, Command):
                value.bind(self)
                self.commands.append(value)

            elif isinstance(value, Task):
                value.bind(self)
                self.tasks.append(value)

    async def setup(self):
        pass

    @staticmethod
    def command(_next, **kwargs):
        if _next is not None:
            return construct_command(_next, **kwargs)

        else:
            def predicate(_next):
                return construct_command(_next, **kwargs)

            return predicate

    @staticmethod
    def task(**kwargs):
        def predicate(_next):
            return Task(_next, **kwargs)

        return predicate
