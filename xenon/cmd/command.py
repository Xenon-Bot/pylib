from abc import ABC
import inspect
import asyncio
import types
import time

from .. import rest, Message

from .enums import *
from .data import *
from .util import *
from .converter import *
from .checks import *


__all__ = (
    "inspect_options",
    "Command",
    "Option",
    "SubCommand",
    "SubCommandGroup",
    "Choice",
    "Converter",
    "inspect_checks",
    "construct_command"
)


def inspect_options(_callable, descriptions=None):
    descriptions = descriptions or {}
    skip = 1
    if inspect.ismethod(_callable):
        skip += 1

    options = []
    for p in list(inspect.signature(_callable).parameters.values())[skip:]:
        converter = p.annotation if p.annotation != inspect.Parameter.empty else str
        _type = CommandOptionType.STRING
        choices = []
        if converter == int:
            _type = CommandOptionType.INTEGER

        elif converter == bool:
            _type = CommandOptionType.BOOLEAN

        elif isinstance(converter, tuple) or isinstance(converter, list):
            for choice in converter:
                choices.append(Choice(name="placeholder", value=choice))

            converter = str

        elif inspect.isclass(converter) and issubclass(converter, Converter):
            _type = converter.type

        options.append(Option(
            type=_type,
            name=p.name,
            description=descriptions.get(p.name, "No description"),
            default=False,
            required=p.default == inspect.Parameter.empty,
            choices=choices,
            converter=converter
        ))

    return options


def inspect_checks(_next):
    checks = []
    while isinstance(_next, Check):
        checks.append(_next)
        _next = _next.next

    return _next, checks


def parse_docstring(doc):
    description = doc.splitlines()[0]
    long_description = ""
    options = {}
    in_args = False
    for line in doc.splitlines():
        if line == "---":
            in_args = not in_args

        elif in_args:
            name, desc = line.split("->")
            options[name.strip()] = desc.strip()
            long_description += f"**{name.strip()}**: *{desc.strip()}*\n"

        else:
            long_description += f"{line}\n"

    return description, long_description, options


def construct_command(_next, **kwargs):
    _callable, checks = inspect_checks(_next)
    parsed_doc = parse_docstring(kwargs.get("description", inspect.getdoc(_callable)))
    return Command(
        name=kwargs.get("name", _callable.__name__),
        description=parsed_doc[0],
        callable=_callable,
        checks=checks,
        options=kwargs.get("options", inspect_options(_callable, parsed_doc[2])),
        help_text=parsed_doc[1],
        **kwargs
    )


def _construct_sub_command(_next, **kwargs):
    _callable, checks = inspect_checks(_next)
    parsed_doc = parse_docstring(kwargs.get("description", inspect.getdoc(_callable)))
    return SubCommand(
        name=kwargs.get("name", _callable.__name__),
        description=parsed_doc[0],
        callable=_callable,
        checks=checks,
        options=kwargs.get("options", inspect_options(_callable, parsed_doc[2])),
        help_text=parsed_doc[1],
        **kwargs
    )


def _construct_sub_group(_next, **kwargs):
    _callable, checks = inspect_options(_next)
    parsed_doc = parse_docstring(kwargs.get("description", inspect.getdoc(_callable)))
    return SubCommandGroup(
        name=kwargs.get("name", _callable.__name__),
        description=parsed_doc[0],
        callable=_callable,
        checks=checks,
        options=kwargs.get("options", inspect_options(_callable, parsed_doc[2])),
        help_text=parsed_doc[1],
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
        self.help_text = kwargs.get("help_text")

        self.bot = kwargs.get("bot")

    def __iter__(self):
        yield from {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "options": [dict(o) for o in self.options]
        }.items()

    def bind(self, obj):
        self.options.pop(0)  # Options have to be shifted to respect the self parameter
        for option in self.options:
            if isinstance(option, SubCommand):
                option.bind(obj)

            elif isinstance(option, SubCommandGroup):
                option.bind(obj)

        self.callable = types.MethodType(self.callable, obj)

    def sub_command(self, _next=None, **kwargs):
        if _next is not None:
            opt = _construct_sub_command(_next, parent=self, **kwargs)
            self.options.append(opt)
            return opt

        else:
            def predicate(_next):
                opt = _construct_sub_command(_next, parent=self, **kwargs)
                self.options.append(opt)
                return opt

            return predicate

    def sub_group(self, _next=None, **kwargs):
        if _next is not None:
            opt = _construct_sub_group(_next, parent=self, **kwargs)
            self.options.append(opt)
            return opt

        else:
            def predicate(_next):
                opt = _construct_sub_group(_next, parent=self, **kwargs)
                self.options.append(opt)
                return opt

            return predicate

    async def execute(self, data):
        outdated_resp = InteractionResponse.respond_and_eat(
            content="Discords command cache seems to be outdated, you might have to wait up to one hour ...",
            ephemeral=True
        )
        ctx = Context(data, self)

        async def _wrapped_callable(_callable):
            try:
                result = await _callable
                if not ctx.future.done():
                    ctx.future.set_result(result)

            except Exception as e:
                if not ctx.future.done():
                    ctx.future.set_exception(e)

                else:
                    raise e

        try:
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

                        sub_options.append(inner_match.converter(inner_option.value))

                    for check in match.checks:
                        await check.run(ctx, *sub_options)

                    self.bot.loop.create_task(_wrapped_callable(match.callable(ctx, *sub_options)))
                    return await ctx.future

                if isinstance(match, SubCommandGroup):
                    # TODO: Recursive option discovery
                    pass

                else:
                    options.append(match.converter(option.value))

            for check in self.checks:
                await check.run(ctx, *options)

            self.bot.loop.create_task(_wrapped_callable(self.callable(ctx, *options)))
            return await ctx.future
        except Exception as e:
            if not ctx.future.done():
                ctx.initial_response = time.perf_counter()  # TODO: Remove when discords PR has shipped
                ctx.future.cancel()

            self.bot.loop.create_task(self.bot.command_error(ctx, e))
            return InteractionResponse.ack()


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

        self.checks = kwargs.get("checks")
        self.help_text = kwargs.get("help_text")

    def __iter__(self):
        yield from super().__iter__()
        yield "options", [dict(o) for o in self.options]

    def bind(self, obj):
        self.options.pop(0)  # Options have to be shifted to respect the self parameter
        self.callable = types.MethodType(self.callable, obj)


class SubCommandGroup(BaseOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = CommandOptionType.SUB_COMMAND_GROUP
        self.options = kwargs.get("options", [])
        self.callable = kwargs.get("callable")
        self.parent = kwargs.get("parent")

        self.checks = kwargs.get("checks")
        self.help_text = kwargs.get("help_text")

    def __iter__(self):
        yield from super().__iter__()
        yield "options", [dict(o) for o in self.options]

    def sub_command(self, _callable, **kwargs):
        if _callable is not None:
            opt = _construct_sub_command(_callable, **kwargs)
            self.options.append(opt)
            return opt

        else:
            def predicate(_next):
                opt = _construct_sub_command(_callable, **kwargs)
                self.options.append(opt)
                return opt

            return predicate

    def bind(self, obj):
        self.options.pop(0)  # Options have to be shifted to respect the self parameter
        for option in self.options:
            if isinstance(option, SubCommand):
                option.bind(obj)

            elif isinstance(option, SubCommandGroup):
                option.bind(obj)

        self.callable = types.MethodType(self.callable, obj)


class Context:
    def __init__(self, data, cmd):
        self.data = data
        self.cmd = cmd

        self.future = asyncio.Future()
        self.initial_response = None

        self._entity_cache = {}

    async def wait_for_token(self):
        if self.initial_response is None:
            self.initial_response = time.perf_counter()
            return

        delta = time.perf_counter() - self.initial_response
        if delta < 0.5:
            await asyncio.sleep(0.5 - delta)

    @property
    def member(self):
        return self.data.member

    @property
    def author(self):
        return self.data.member

    @property
    def bot(self):
        return self.cmd.bot

    @property
    def token(self):
        return self.data.token

    @property
    def channel_id(self):
        return self.data.channel_id

    @property
    def guild_id(self):
        return self.data.guild_id

    async def ack(self):
        if not self.future.done():
            self.future.set_result(InteractionResponse.ack())

    async def get_full_guild(self, cache=True):
        guild = await self.get_guild(cache)
        guild.channels = await self.get_guild_channels(cache)
        return guild

    async def get_guild(self, cache=True):
        if cache and "guild" in self._entity_cache:
            return self._entity_cache["guild"]

        result = await self.bot.http.get_guild(self.guild_id)
        self._entity_cache["guild"] = result
        return result

    async def get_guild_roles(self, cache=True):
        if cache and "roles" in self._entity_cache:
            return self._entity_cache["roles"]

        result = await self.bot.http.get_guild_roles(self.guild_id)
        self._entity_cache["roles"] = result
        return result

    async def get_guild_channels(self, cache=True):
        if cache and "channels" in self._entity_cache:
            return self._entity_cache["channels"]

        result = await self.bot.http.get_guild_channels(self.guild_id)
        self._entity_cache["channels"] = result
        return result

    async def get_channel(self, cache=True):
        if cache and "channel" in self._entity_cache:
            return self._entity_cache["channel"]

        result = await self.bot.http.get_channel(self.channel_id)
        self._entity_cache["channel"] = result
        return result

    async def respond_and_eat(self, content=None, **data):
        await self.wait_for_token()
        data["content"] = content
        response = InteractionResponse(InteractionResponseType.CHANNEL_MESSAGE, data)
        if not self.future.done():
            self.future.set_result(response)

        else:
            req = rest.Request("POST",
                               "/webhooks/{application_id}/{token}",
                               application_id=self.bot.user.id, token=self.token)
            self.bot.http.start_request(req, json=response.data)
            return await req

    async def respond(self, content=None, wait=False, **data):
        await self.wait_for_token()
        data["content"] = content
        response = InteractionResponse(InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE, data)
        if not self.future.done():
            self.future.set_result(response)

        else:
            req = rest.Request("POST",
                               "/webhooks/{application_id}/{token}",
                               application_id=self.bot.user.id, token=self.token)
            self.bot.http.start_request(req, json=response.data, params={"wait": "true" if wait else "false"})
            res = await req
            if res is not None:
                return Message(res)

    async def edit_response(self, content=None, message_id="@original", **data):
        await self.wait_for_token()
        data["content"] = " " if content == "" else content  # removing message content is weird
        response = InteractionResponse(InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE, data)
        req = rest.Request("PATCH",
                           "/webhooks/{application_id}/{token}/messages/{message_id}",
                           application_id=self.bot.user.id, token=self.token, message_id=message_id)
        self.bot.http.start_request(req, json=response.data)
        return await req

    async def delete_response(self, message_id="@original"):
        await self.wait_for_token()
        req = rest.Request("DELETE",
                           "/webhooks/{application_id}/{token}/messages/{message_id}",
                           application_id=self.bot.user.id, token=self.token, message_id=message_id)
        self.bot.http.start_request(req)
        return await req

    async def get_response(self, message_id="@original"):
        await self.wait_for_token()
        req = rest.Request("PATCH",
                           "/webhooks/{application_id}/{token}/messages/{message_id}",
                           application_id=self.bot.user.id, token=self.token, message_id=message_id, converter=Message)
        self.bot.http.start_request(req, json={})
        return await req
