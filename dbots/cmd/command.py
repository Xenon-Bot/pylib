from enum import IntEnum
import inspect
import re
import types

from .errors import *
from .checks import *

__all__ = (
    "make_command",
    "Command",
    "CommandOption",
    "CommandOptionType",
    "CommandOptionChoice",
    "SubCommand",
    "SubCommandGroup"
)


def inspect_options(_callable, extends=None):
    extends = extends or {}
    options = []
    for p in list(inspect.signature(_callable).parameters.values()):
        if p.name in {"self", "ctx"}:
            continue

        converter = p.annotation if p.annotation != inspect.Parameter.empty else str
        _type = CommandOptionType.STRING
        if isinstance(converter, CommandOptionType):
            _type = converter
            if converter in {CommandOptionType.ROLE, CommandOptionType.CHANNEL, CommandOptionType.USER}:
                def snowflake_finder(v):
                    id_match = re.match(r"[0-9]+", v)
                    if id_match is None:
                        raise NotASnowflake(v)

                    return id_match[0]

                converter = snowflake_finder

            if converter == CommandOptionType.INTEGER:
                converter = int

            if converter == CommandOptionType.BOOLEAN:
                converter = bool

        elif converter == int:
            _type = CommandOptionType.INTEGER

        elif converter == bool:
            _type = CommandOptionType.BOOLEAN

        # elif inspect.isclass(converter) and issubclass(converter, Converter):
        #     _type = converter.type

        extend = extends.get(p.name, {})
        if type(extend) == str:
            extend = {"description": extend}

        options.append(CommandOption(
            type=_type,
            name=p.name,
            description=extend.get("description", "No description"),
            # default=False,
            required=p.default == inspect.Parameter.empty,
            choices=[CommandOptionChoice(*o) for o in extend.get("choices", [])],
            converter=converter
        ))

    return options


def make_command(klass, cb, **kwargs):
    checks = []
    while isinstance(cb, Check):
        checks.append(cb)
        cb = cb.next

    doc_lines = inspect.cleandoc(inspect.getdoc(cb)).splitlines()
    values = {
        "callable": cb,
        "name": cb.__name__,
        "description": doc_lines[0],
        "long_description": "\n".join(doc_lines),
        "options": inspect_options(cb, extends=kwargs.get("extends")),
        "checks": checks
    }

    values.update(kwargs)
    return klass(**values)


class Command:
    def __init__(self, **kwargs):
        self.callable = kwargs.get("callable")
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.long_description = kwargs.get("long_description")
        self.options = kwargs.get("options", [])
        self.sub_commands = []

        self.visible = kwargs.get("visible", True)
        self.checks = kwargs.get("checks", [])
        self.guild_id = kwargs.get("guild_id")
        self.register = kwargs.get("register", True)
        self.ephemeral = kwargs.get("ephemeral", False)

    @property
    def full_name(self):
        return self.name

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)
        for sub_command in self.sub_commands:
            sub_command.bind(obj)

    def sub_command_group(self, _callable=None, **kwargs):
        if _callable is None:
            def _predicate(_callable):
                cmd = make_command(SubCommandGroup, _callable, **kwargs)
                cmd.parent = self
                self.sub_commands.append(cmd)
                return cmd

            return _predicate

        cmd = make_command(SubCommandGroup, _callable, **kwargs)
        cmd.parent = self
        self.sub_commands.append(cmd)
        return cmd

    def sub_command(self, _callable=None, **kwargs):
        if _callable is None:
            def _predicate(_callable):
                cmd = make_command(SubCommand, _callable, **kwargs)
                cmd.parent = self
                self.sub_commands.append(cmd)
                return cmd

            return _predicate

        cmd = make_command(SubCommand, _callable, **kwargs)
        cmd.parent = self
        self.sub_commands.append(cmd)
        return cmd

    def to_payload(self):
        return {
            "name": self.name,
            "description": self.description,
            "options": [o.to_payload() for o in self.options] + [s.to_payload() for s in self.sub_commands],
            "default_permission": self.visible
        }


class CommandOptionType(IntEnum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class CommandOption:
    def __init__(self, **kwargs):
        self.type = kwargs["type"]
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.default = kwargs.get("default", False)
        self.required = kwargs.get("required", True)
        self.choices = kwargs.get("choices", [])

        self.converter = kwargs.get("converter", str)

    def to_payload(self):
        return {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "default": self.default,
            "required": self.required,
            "choices": [c.to_payload() for c in self.choices]
        }


class SubCommand:
    def __init__(self, **kwargs):
        self.callable = kwargs.get("callable")
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.long_description = kwargs.get("long_description")
        self.options = kwargs.get("options", [])

        self.parent = kwargs.get("parent")
        self.checks = kwargs.get("checks", [])
        self.ephemeral = kwargs.get("ephemeral", False)

    @property
    def full_name(self):
        return f"{self.parent.full_name} {self.name}"

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)

    def to_payload(self):
        return {
            "type": CommandOptionType.SUB_COMMAND,
            "name": self.name,
            "description": self.description,
            "options": [o.to_payload() for o in self.options]
        }


class SubCommandGroup:
    def __init__(self, **kwargs):
        self.callable = kwargs.get("callable")
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.long_description = kwargs.get("long_description")
        self.options = kwargs.get("options", [])
        self.sub_commands = []

        self.parent = kwargs.get("parent")
        self.checks = kwargs.get("checks", [])
        self.ephemeral = kwargs.get("ephemeral", False)

    @property
    def full_name(self):
        return f"{self.parent.full_name} {self.name}"

    def bind(self, obj):
        self.callable = types.MethodType(self.callable, obj)
        for sub_command in self.sub_commands:
            sub_command.bind(obj)

    def sub_command(self, _callable=None, **kwargs):
        if _callable is None:
            def _predicate(_callable):
                cmd = make_command(SubCommand, _callable, **kwargs)
                cmd.parent = self
                self.sub_commands.append(cmd)
                return cmd

            return _predicate

        cmd = make_command(SubCommand, _callable, **kwargs)
        cmd.parent = self
        self.sub_commands.append(cmd)
        return cmd

    def to_payload(self):
        return {
            "type": CommandOptionType.SUB_COMMAND_GROUP,
            "name": self.name,
            "description": self.description,
            "options": [o.to_payload() for o in self.options] + [s.to_payload() for s in self.sub_commands]
        }


class CommandOptionChoice:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_payload(self):
        return {
            "name": self.name,
            "value": self.value
        }
