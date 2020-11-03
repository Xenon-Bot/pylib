from abc import ABC
import inspect

from .enums import *
from .data import *
from .util import *


__all__ = (
    "inspect_options",
    "Command",
    "Option",
    "SubCommand",
    "SubCommandGroup",
    "Choice",
    "Converter"
)


def inspect_options(_callable):
    skip = 1
    if inspect.ismethod(_callable):
        skip += 1

    options = []
    for p in list(inspect.signature(_callable).parameters.values())[skip:]:
        converter = p.annotation if p.annotation != inspect.Parameter.empty else None
        _type = CommandOptionType.STRING
        choices = []
        if converter == int:
            _type = CommandOptionType.INTEGER

        elif converter == bool:
            _type = CommandOptionType.BOOLEAN

        elif isinstance(converter, tuple) or isinstance(converter, list):
            for choice in converter:
                choices.append(Choice(name="placeholder", value=choice))

        elif isinstance(converter, Converter):
            _type = converter.type

        options.append(Option(
            type=_type,
            name=p.name,
            description="placeholder",
            default=False,
            required=p.default == inspect.Parameter.empty,
            choices=choices,
            converter=converter
        ))

    return options


def _construct_sub_command(_callable, **kwargs):
    return SubCommand(
        name=kwargs.get("name", _callable.__name__),
        description=kwargs.get("description", inspect.getdoc(_callable)),
        callable=_callable,
        options=kwargs.get("options", inspect_options(_callable)),
        **kwargs
    )


def _construct_sub_group(_callable, **kwargs):
    return SubCommandGroup(
        name=kwargs.get("name", _callable.__name__),
        description=kwargs.get("description", inspect.getdoc(_callable)),
        callable=_callable,
        options=kwargs.get("options", inspect_options(_callable)),
        **kwargs
    )


class Command:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.options = kwargs.get("options", [])

        self.callable = kwargs.get("callable")
        self.checks = kwargs.get("checks", [])

        self.bot = kwargs.get("bot")

    def __iter__(self):
        yield from {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "options": [dict(o) for o in self.options]
        }.items()

    def sub_command(self, _callable, **kwargs):
        if _callable is not None:
            opt = _construct_sub_command(_callable, parent=self, **kwargs)
            self.options.append(opt)
            return opt

        else:
            def predicate(_callback):
                opt = _construct_sub_command(_callable, parent=self, **kwargs)
                self.options.append(opt)
                return opt

            return predicate

    def sub_group(self, _callable, **kwargs):
        if _callable is not None:
            opt = _construct_sub_group(_callable, parent=self, **kwargs)
            self.options.append(opt)
            return opt

        else:
            def predicate(_callback):
                opt = _construct_sub_group(_callable, parent=self, **kwargs)
                self.options.append(opt)
                return opt

            return predicate

    async def execute(self, data):
        outdated_resp = InteractionResponse.eat_cmd(
            content="Discords command cache seems to be outdated, you might have to wait up to one hour ...",
            ephemeral=True
        )
        ctx = None

        options = []
        for option in data.data.options:
            match = list_get(self.options, name=option.name)
            if match is None:
                return outdated_resp

            if isinstance(match, SubCommand):
                sub_options = []
                for inner_option in option.options:
                    inner_match = list_get(match.options, name=inner_option.name)
                    if inner_match is None:
                        return outdated_resp

                    # TODO: Run converters
                    sub_options.append(inner_option.value)

                return await match.callable(ctx, *sub_options)

            if isinstance(match, SubCommandGroup):
                # TODO: Recursive option discovery
                pass

            else:
                # TODO: Run converters
                options.append(option.value)

        return await self.callable(ctx, *options)


class BaseOption(ABC):
    def __init__(self, **kwargs):
        self.type = kwargs.get("type")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")

    def __iter__(self):
        yield from {
            "type": self.type.value,
            "name": self.name,
            "description": self.description
        }.items()


class Option(BaseOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default = kwargs.get("kwargs", False)
        self.required = kwargs.get("required", False)
        self.choices = kwargs.get("choices")
        self.converter = kwargs.get("converter", str)

    def __iter__(self):
        yield from super().__iter__()
        yield from {
            "default": self.default,
            "required": self.required,
            "choices": [dict(c) for c in self.choices] if self.choices is not None else None
        }.items()


class Choice:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.value = kwargs.get("value")

    def __iter__(self):
        yield from {
            "name": self.name,
            "value": self.value
        }.items()


class SubCommand(BaseOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = CommandOptionType.SUB_COMMAND
        self.options = kwargs.get("options", [])
        self.callable = kwargs.get("callable")
        self.parent = kwargs.get("parent")

    def __iter__(self):
        yield from super().__iter__()
        yield "options", [dict(o) for o in self.options]


class SubCommandGroup(BaseOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = CommandOptionType.SUB_COMMAND_GROUP
        self.options = kwargs.get("options", [])
        self.callable = kwargs.get("callable")
        self.parent = kwargs.get("parent")

    def __iter__(self):
        yield from super().__iter__()
        yield "options", [dict(o) for o in self.options]

    def sub_command(self, _callable, **kwargs):
        if _callable is not None:
            opt = _construct_sub_command(_callable, **kwargs)
            self.options.append(opt)
            return opt

        else:
            def predicate(_callback):
                opt = _construct_sub_command(_callable, **kwargs)
                self.options.append(opt)
                return opt

            return predicate


class Converter:
    type: CommandOptionType


class Context:
    async def respond(self):
        # edit existing one or make new one
        pass
