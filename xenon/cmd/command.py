from abc import ABC
import inspect
import asyncio
import types

from .. import rest

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


def inspect_options(_callable):
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
            description="placeholder",
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


def construct_command(_next, **kwargs):
    _callable, checks = inspect_checks(_next)
    return Command(
        name=kwargs.get("name", _callable.__name__),
        description=kwargs.get("description", inspect.getdoc(_callable)),
        callable=_callable,
        checks=checks,
        options=kwargs.get("options", inspect_options(_callable)),
        **kwargs
    )


def _construct_sub_command(_next, **kwargs):
    _callable, checks = inspect_options(_next)
    return SubCommand(
        name=kwargs.get("name", _callable.__name__),
        description=kwargs.get("description", inspect.getdoc(_callable)),
        callable=_callable,
        checks=checks,
        options=kwargs.get("options", inspect_options(_callable)),
        **kwargs
    )


def _construct_sub_group(_next, **kwargs):
    _callable, checks = inspect_options(_next)
    return SubCommandGroup(
        name=kwargs.get("name", _callable.__name__),
        description=kwargs.get("description", inspect.getdoc(_callable)),
        callable=_callable,
        checks=checks,
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

    def bind(self, obj):
        self.options.pop(0)  # Options have to be shifted to respect the self parameter
        self.callable = types.MethodType(self.callable, obj)

    def sub_command(self, _next, **kwargs):
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

    def sub_group(self, _next, **kwargs):
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
            return await self.bot.command_error(ctx, e)


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

        self.checks = kwargs.get("checks")

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


class Context:
    def __init__(self, data, cmd):
        self.data = data
        self.cmd = cmd

        self.future = asyncio.Future()

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

    async def ack(self):
        if not self.future.done():
            self.future.set_result(InteractionResponse.ack())

    async def respond_and_eat(self, **data):
        response = InteractionResponse(InteractionResponseType.CHANNEL_MESSAGE, data)
        if not self.future.done():
            self.future.set_result(response)

        else:
            req = rest.Request("POST",
                               "/webhooks/{application_id}/{token}",
                               application_id=self.bot.user.id, token=self.token)
            self.bot.http.start_request(req, json=response.data)
            return await req

    async def respond(self, **data):
        response = InteractionResponse(InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE, data)
        if not self.future.done():
            self.future.set_result(response)

        else:
            req = rest.Request("POST",
                               "/webhooks/{application_id}/{token}",
                               application_id=self.bot.user.id, token=self.token)
            self.bot.http.start_request(req, json=response.data)
            return await req

    async def edit_response(self, message_id="@original", **data):
        response = InteractionResponse(InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE, data)
        req = rest.Request("PATCH",
                           "/webhooks/{application_id}/{token}/messages/{message_id}",
                           application_id=self.bot.user.id, token=self.token, message_id=message_id)
        self.bot.http.start_request(req, json=response.data)
        return await req
