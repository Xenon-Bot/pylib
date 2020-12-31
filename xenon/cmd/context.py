import dc_interactions as dc

from ..entities import *


__all__ = (
    "CustomContext",
)


class CustomContext(dc.CommandContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http_cache = {}

    @property
    def author(self):
        return Member(self.payload.member)

    @property
    def member(self):
        return Member(self.payload.member)

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

        member = await self.bot.http.get_guild_member(self.guild_id, self.bot.app_id)
        self._http_cache["member"] = member
        return member
