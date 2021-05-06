from enum import IntEnum
import asyncio

from .response import *
from ..rest import *


__all__ = (
    "CommandContext",
    "ContextState",
    "ButtonContext"
)


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


class ButtonContext:
    def __init__(self, bot, button, payload):
        self.bot = bot
        self.button = button
        self.payload = payload
        self._http_cache = {}

        self.state = ContextState.NOT_REPLIED
        self._future = bot.loop.create_future()

    @property
    def custom_id(self):
        return self.payload.data.custom_id

    async def update(self, *args, **kwargs):
        resp = InteractionResponse.message_update(*args, **kwargs)
        if self.state != ContextState.DEFERRED:
            self.state = ContextState.REPLIED
            self._future.set_result(resp)
        else:
            return await self.bot.http.edit_interaction_response(
                self.token,
                "@original",
                files=resp.files if len(resp.files) > 0 else None,
                **resp.data
            )

    def defer(self, *args, **kwargs):
        if self.state == ContextState.NOT_REPLIED:
            resp = InteractionResponse.defer_message_update(*args, **kwargs)
            self._future.set_result(resp)
            self.state = ContextState.DEFERRED

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
