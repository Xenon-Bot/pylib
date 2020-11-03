from aiohttp import web
import asyncio
import inspect
import ed25519
import json
import traceback
import sys

from .. import rest
from ..entities import Snowflake

from .enums import *
from .data import *
from .command import *


__all__ = (
    "Bot",
)


# help command could use choices for command names


class Bot:
    def __init__(self, **kwargs):
        self.loop = kwargs.get("loop", asyncio.get_event_loop())
        self.http = kwargs.get("http")
        self.public_key = ed25519.VerifyingKey(kwargs.get("public_key"), encoding="hex")
        self.user = None

        self._commands = []

        self._web = web.Application()
        self._web.add_routes([web.post("/webh", self.webhook_entry)])

    async def command_received(self, data):
        command_id = data.data.id
        for cmd in self._commands:
            if command_id == cmd.id:
                return await cmd.execute(data)

    async def command_error(self, ctx, e):
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(tb, file=sys.stderr)
        return InteractionResponse.respond_and_eat(
            content=f"__**Unexpected Error**__```py\n{e.__class__.__name__}:\n{str(tb)}```",
            ephemeral=True
        )

    async def webhook_entry(self, req):
        raw_data = await req.read()
        print(json.dumps(json.loads(raw_data), indent=2))
        signature = req.headers.get("x-signature-ed25519")
        if signature is None:
            return web.HTTPUnauthorized()

        try:
            self.public_key.verify(signature, raw_data, encoding="hex")
        except ed25519.BadSignatureError:
            return web.HTTPUnauthorized()

        data = InteractionData(json.loads(raw_data))
        response = InteractionResponse.pong()
        if data.type == InteractionType.APPLICATION_COMMAND:
            response = await self.command_received(data)

        return web.json_response(dict(response))

    async def start(self, *args, **kwargs):
        self.user = await self.http.get_me()
        await self.load_commands()

        self._web.runner = runner = web.AppRunner(self._web)
        await runner.setup()
        site = web.TCPSite(runner, *args, **kwargs)
        await site.start()

    async def stop(self):
        if self._web.runner is not None:
            await self._web.runner.cleanup()

    def run(self, *args, **kwargs):
        self.loop.create_task(self.start(*args, **kwargs))
        self.loop.run_forever()

    def add_command(self, cmd):
        cmd.bot = self
        self._commands.append(cmd)

    def remove_command(self, cmd):
        cmd.bot = None
        self._commands.remove(cmd)

    def add_module(self, module):
        for cmd in module.commands:
            self.add_command(cmd)

        for task in module.tasks:
            task.start(self.loop)

    def remove_module(self, module):
        for cmd in module.commands:
            self.remove_command(cmd)

        for task in module.tasks:
            task.stop()

    def command(self, _next, **kwargs):
        if _next is not None:
            cmd = construct_command(_next, **kwargs)
            self.add_command(cmd)
            return cmd

        else:
            def predicate(_next):
                cmd = construct_command(_next, **kwargs)
                self.add_command(cmd)
                return cmd

            return predicate

    def fetch_commands(self):
        req = rest.Request("GET", "/applications/{application_id}/guilds/496683369665658880/commands", application_id=self.user.id)
        self.http.start_request(req)
        return req

    async def unregister_command(self, cmd):
        req = rest.Request("DELETE", "/applications/{application_id}/guilds/496683369665658880/commands/{command_id}",
                           application_id=self.user.id, command_id=cmd.id)
        self.http.start_request(req)
        result = await req
        cmd.id = None
        return result

    async def register_command(self, cmd):
        req = rest.Request("POST", "/applications/{application_id}/guilds/496683369665658880/commands",
                           application_id=self.user.id)
        self.http.start_request(req, json=dict(cmd))
        result = await req
        cmd.id = result["id"]
        return result

    async def update_command(self, command_id, cmd):
        req = rest.Request("PATCH", "/applications/{application_id}/guilds/496683369665658880/commands/{command_id}",
                           application_id=self.user.id, command_id=command_id)
        self.http.start_request(req, json=dict(cmd))
        result = await req
        cmd.id = result["id"]
        return result

    async def load_commands(self):
        existing = await self.fetch_commands()
        for cmd in filter(lambda c: c.id is None, self._commands):
            for i, ex_cmd in enumerate(existing):
                if cmd.name == ex_cmd["name"]:
                    await self.update_command(ex_cmd["id"], cmd)
                    existing.pop(i)
                    break

            else:
                await self.register_command(cmd)

        for ex_cmd in existing:
            await self.unregister_command(Snowflake(ex_cmd["id"]))
