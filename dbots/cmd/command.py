from enum import IntEnum
import inspect
import re
import types
import asyncio

from .response import *
from .errors import *
from .checks import *
from ..rest import *

__all__ = (
    "make_command",
    "Command",
    "CommandOption",
    "CommandOptionType",
    "CommandOptionChoice",
    "SubCommand",
    "SubCommandGroup",
    "CommandContext",
    "ContextState"
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


class ContextState(IntEnum):
    NOT_REPLIED = 0
    DEFERRED = 1
    REPLIED = 2


class CommandContext:
    def __init__(self, bot, command, payload, args):
        self.bot = bot
        self.payload = payload
        self.command = command
        self.args = args
        self._http_cache = {}

        self.state = ContextState.NOT_REPLIED
        self._future = bot.loop.create_future()

    async def respond(self, *args, **kwargs):
        resp = InteractionResponse.message(*args, **kwargs)
        if self.state == ContextState.NOT_REPLIED and len(resp.files) != 0:
            self.defer()

        if self.state == ContextState.NOT_REPLIED:
            self._future.set_result(resp)
            self.state = ContextState.REPLIED
        elif self.state == ContextState.DEFERRED:
            result = await self.edit_response(*args, message_id="@original", **kwargs)
            self.state = ContextState.REPLIED
            return result
        else:
            result = await self.bot.http.create_interaction_response(
                self.token,
                files=resp.files if len(resp.files) > 0 else None,
                **resp.data
            )
            self.state = ContextState.REPLIED
            return result

    def defer(self, *args, **kwargs):
        if self.state == ContextState.NOT_REPLIED:
            resp = InteractionResponse.defer(*args, **kwargs)
            self._future.set_result(resp)
            self.state = ContextState.DEFERRED

    async def get_response(self, message_id="@original"):
        for i in range(3):
            try:
                return await self.bot.http.get_interaction_response(self.token, message_id)
            except HTTPNotFound:
                if message_id != "@original" or i == 2:
                    raise

                await asyncio.sleep(0.3 * (i + 1))

    async def edit_response(self, *args, message_id="@original", **kwargs):
        resp = InteractionResponse.message(*args, **kwargs)
        for i in range(3):
            try:
                return await self.bot.http.edit_interaction_response(
                    self.token,
                    message_id,
                    files=resp.files if len(resp.files) > 0 else None,
                    **resp.data
                )
            except HTTPNotFound:
                if message_id != "@original" or i == 2:
                    raise

                await asyncio.sleep(0.3 * (i + 1))
                continue

    async def delete_response(self, message_id="@original"):
        for i in range(3):
            try:
                return await self.bot.http.delete_interaction_response(self.token, message_id)
            except HTTPNotFound:
                if message_id != "@original" or i == 2:
                    raise

                await asyncio.sleep(0.3 * (i + 1))
                continue

    async def wait(self):
        return await self._future

    async def fetch_channel(self):
        if "channel" in self._http_cache:
            return self._http_cache["channel"]

        channel = await self.bot.http.get_channel(self.channel_id)
        self._http_cache["channel"] = channel
        return channel

    async def fetch_guild(self):
        if "guild" in self._http_cache:
            return self._http_cache["guild"]

        guild = await self.bot.http.get_guild(self.guild_id)
        self._http_cache["guild"] = guild
        self._http_cache["roles"] = guild.roles
        return guild

    async def fetch_guild_channels(self):
        if "channels" in self._http_cache:
            return self._http_cache["channels"]

        channels = await self.bot.http.get_guild_channels(self.guild_id)
        self._http_cache["channels"] = channels
        return channels

    async def fetch_guild_roles(self):
        if "roles" in self._http_cache:
            return self._http_cache["roles"]

        roles = await self.bot.http.get_guild_roles(self.guild_id)
        self._http_cache["roles"] = roles
        return roles

    async def fetch_bot_member(self):
        if "member" in self._http_cache:
            return self._http_cache["member"]

        member = await self.bot.http.get_guild_member(self.guild_id, self.bot.http.application_id)
        self._http_cache["member"] = member
        return member

    def __getattr__(self, item):
        return getattr(self.payload, item)
