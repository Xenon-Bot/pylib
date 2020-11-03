from aiohttp import web
import asyncio
import inspect

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
        self.user = None

        self._loaded_commands = []
        self.commands = []

        self._web = web.Application()
        self._web.add_routes([web.post("/webh", self.webhook_entry)])
        self._runner = None

    async def command_received(self, data):
        pass

    async def webhook_entry(self, req):
        data = InteractionData(await req.json())
        if data.type == InteractionType.PING:
            return web.json_response({"type": InteractionResponseType.PONG})

        elif data.type == InteractionType.APPLICATION_COMMAND:
            return await self.command_received(data)

    async def start(self, *args, **kwargs):
        self.user = await self.http.get_me()
        await self.load_commands()

        runner = web.AppRunner(self._web)
        await runner.setup()
        site = web.TCPSite(runner, *args, **kwargs)
        await site.start()

    async def stop(self):
        if self._runner is not None:
            await self._runner.cleanup()

    def run(self, *args, **kwargs):
        self.loop.create_task(self.start(*args, **kwargs))
        self.loop.run_forever()

    def command(self, _callable, **kwargs):
        def _construct_command(_callback, **kwargs):
            return Command(
                name=kwargs.get("name", _callback.__name__),
                description=kwargs.get("description", inspect.getdoc(_callback)),
                callable=_callable,
                options=kwargs.get("options", inspect_options(_callable))
            )

        if _callable is not None:
            cmd = _construct_command(_callable, **kwargs)
            self.commands.append(cmd)
            return cmd

        else:
            def predicate(_callback):
                cmd = _construct_command(_callable, **kwargs)
                self.commands.append(cmd)
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
        try:
            self._loaded_commands.remove(cmd)
        except ValueError:
            pass
        return result

    async def register_command(self, cmd):
        req = rest.Request("POST", "/applications/{application_id}/guilds/496683369665658880/commands",
                           application_id=self.user.id)
        self.http.start_request(req, json=dict(cmd))
        result = await req
        cmd.id = result["id"]
        self._loaded_commands.append(cmd)
        return result

    async def update_command(self, command_id, cmd):
        req = rest.Request("PATCH", "/applications/{application_id}/guilds/496683369665658880/commands/{command_id}",
                           application_id=self.user.id, command_id=command_id)
        self.http.start_request(req, json=dict(cmd))
        result = await req
        cmd.id = result["id"]
        self._loaded_commands.append(cmd)
        return result

    async def load_commands(self):
        existing = await self.fetch_commands()
        for cmd in self.commands:
            for i, ex_cmd in enumerate(existing):
                if cmd.name == ex_cmd["name"]:
                    await self.update_command(ex_cmd["id"], cmd)
                    existing.pop(i)
                    break

            else:
                await self.register_command(cmd)

        for ex_cmd in existing:
            await self.unregister_command(Snowflake(ex_cmd["id"]))
