import json
from aiohttp import web, ClientSession, ContentTypeError
import asyncio
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import traceback
import sys
import inspect
import aioredis

from ..utils import *
from ..rest import *

from .command import *
from .payloads import *
from .response import *
from .task import *

__all__ = (
    "InteractionBot",
)


class InteractionBot:
    def __init__(self, **kwargs):
        self.commands = []
        self.tasks = []
        self.public_key = VerifyKey(bytes.fromhex(kwargs["public_key"]))
        self.token = kwargs["token"]
        self._loop = kwargs.get("loop")
        self.session = kwargs.get("session", ClientSession(loop=self.loop))
        self.guild_id = kwargs.get("guild_id")  # Can be used during development to avoid the 1 hour cache
        self.app_id = None
        self.ctx_klass = kwargs.get("ctx_klass", CommandContext)

        # Filled by setup()
        self.http = None
        self.redis = None

        self.listeners = {}
        self.modules = set()

    @property
    def loop(self):
        return self._loop or asyncio.get_event_loop()

    def find_command(self, data):
        base_command = iterable_get(self.commands, name=data.name)
        if base_command is None:
            return None  # Out of sync; ignore

        for option in data.options:
            sub_command = iterable_get(base_command.sub_commands, name=option.name)
            if isinstance(sub_command, SubCommandGroup):
                for sub_option in option.options:
                    sub_sub_command = iterable_get(sub_command.sub_commands, name=sub_option.name)
                    if sub_sub_command is None:
                        return None  # Out of sync; ignore

                    return sub_sub_command, sub_option.options

            elif isinstance(sub_command, SubCommand):
                return sub_command, option.options

        return base_command, data.options

    def command(self, _callable=None, **kwargs):
        if _callable is None:
            def _predicate(_callable):
                cmd = make_command(Command, _callable, **kwargs)
                self.commands.append(cmd)
                return cmd

            return _predicate

        return make_command(Command, _callable, **kwargs)

    def task(self, **td):
        def _predicate(_callable):
            t = Task(_callable, **td)
            self.tasks.append(t)
            return t

        return _predicate

    def dispatch(self, event, *args, **kwargs):
        listeners = self.listeners.get(event)
        if listeners is not None:
            for callable, check in listeners:
                try:
                    if check is not None and not check(*args, **kwargs):
                        continue
                except:
                    traceback.print_exc()
                    continue

                if isinstance(callable, asyncio.Future):
                    if not callable.done():
                        if len(args) == 1:
                            callable.set_result(args[0])

                        else:
                            callable.set_result(tuple([*args]))

                else:
                    try:
                        res = callable(*args, **kwargs)
                        if inspect.isawaitable(res):
                            self.loop.create_task(res)
                    except:
                        traceback.print_exc()

    def add_listener(self, event, callable, check=None):
        if event in self.listeners:
            self.listeners[event].add((callable, check))

        else:
            self.listeners[event] = {(callable, check)}

    def remove_listener(self, event, callable, check=None):
        self.listeners[event].remove((callable, check))

    def listener(self, _callable=None, name=None):
        if _callable is None:
            def _predicate(_callable):
                self.add_listener(name or _callable.__name__[3:], _callable)
                return _callable

            return _predicate

        self.add_listener(name or _callable.__name__[3:], _callable)
        return _callable

    async def wait_for(self, event, check=None, timeout=None):
        future = self.loop.create_future()
        try:
            self.add_listener(event, future, check=check)
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self.remove_listener(event, future, check=check)

    def load_module(self, module):
        self.modules.add(module)
        for cmd in module.commands:
            self.commands.append(cmd)

        for t in module.tasks:
            self.tasks.append(t)

    async def on_command_error(self, ctx, e):
        if isinstance(e, asyncio.CancelledError):
            raise e

        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print("Command Error:\n", tb, file=sys.stderr)
        await ctx.defer()

    async def execute_command(self, command, payload, remaining_options):
        ctx = self.ctx_klass(self, command, payload, args=remaining_options)

        async def _executor():
            try:
                values = {}
                for option in remaining_options:
                    matching_option = iterable_get(command.options, name=option.name)
                    if matching_option is not None:
                        value = matching_option.converter(option.value)
                        values[option.name] = value

                for check in command.checks:
                    res = await check.run(ctx, **values)
                    if res is not True:
                        return

                result = command.callable(ctx, **values)
                if inspect.isawaitable(result):
                    await result
            except Exception as e:
                await self.on_command_error(ctx, e)

        self.loop.create_task(_executor())
        if command.auto_defer:
            self.loop.call_later(2, ctx.defer)

        try:
            return await ctx.wait()
        except Exception as e:
            return await self.on_command_error(ctx, e)

    async def interaction_received(self, payload):
        if payload.type == InteractionType.PING:
            return InteractionResponse.pong()

        elif payload.type == InteractionType.APPLICATION_COMMAND:
            command, remaining_options = self.find_command(payload.data)
            if command is None:
                return None

            return await self.execute_command(command, payload, remaining_options)

    async def aiohttp_entry(self, request):
        raw_data = await request.text()
        signature = request.headers.get("x-signature-ed25519")
        timestamp = request.headers.get("x-signature-timestamp")
        if signature is None or timestamp is None:
            return web.HTTPUnauthorized()

        try:
            self.public_key.verify(f"{timestamp}{raw_data}".encode(), bytes.fromhex(signature))
        except BadSignatureError:
            return web.HTTPUnauthorized()

        data = InteractionPayload(json.loads(raw_data))
        resp = await self.interaction_received(data)
        if resp is None:
            return web.json_response({}, status=400)

        return web.json_response(resp.to_dict())

    async def sanic_entry(self, request):
        from sanic import response

        raw_data = request.body.decode("utf-8")
        signature = request.headers.get("x-signature-ed25519")
        timestamp = request.headers.get("x-signature-timestamp")
        if signature is None or timestamp is None:
            return response.empty(status=401)

        try:
            self.public_key.verify(f"{timestamp}{raw_data}".encode(), bytes.fromhex(signature))
        except BadSignatureError:
            return response.empty(status=401)

        data = InteractionPayload(json.loads(raw_data))
        resp = await self.interaction_received(data)
        if resp is None:
            return response.json({}, status=400)

        return response.json(resp.to_dict())

    async def setup(self, redis_url="redis://localhost"):
        self.redis = await aioredis.create_redis_pool(redis_url)
        self.http = HTTPClient(self.token, self.redis)
        app = await self.http.get_application()
        self.http.application_id = app["id"]
        for t in self.tasks:
            self.loop.create_task(t.run())

        for module in self.modules:
            self.loop.create_task(module.post_setup())

    def _commands_endpoint(self, guild_id=None):
        if guild_id is not None or self.guild_id is not None:
            return "/applications/{app_id}/guilds/{guild_id}/commands"
        else:
            return "/applications/{app_id}/commands"

    async def push_commands(self):
        data = [c.to_payload() for c in self.commands if c.register]
        if self.guild_id is None:
            await self.http.replace_global_commands(data)

        else:
            await self.http.replace_guild_commands(self.guild_id, data)
