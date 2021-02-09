import asyncio
from collections import OrderedDict
import traceback
import orjson

from ..rest import *
from ..enums import *

__all__ = (
    "GuildSaver",
    "LoaderOptions",
    "RoleRateLimit",
    "GuildLoader",
    "run_loader",
    "warning_text",
    "status_text",
    "option_text"
)


async def create_chatlog(http, channel_id, count, before=None):
    pass


async def load_chatlog(http, channel_id, messages):
    pass


class GuildSaver:
    def __init__(self, bot, guild_id):
        self.http = bot.http
        self.guild_id = guild_id
        self.guild = None
        self.chatlog = 0
        self.data = {}

    async def _save_base(self):
        self.data.update({
            k: v
            for k, v in self.guild.to_dict().items()
            if k in {
                "id", "name", "icon", "owner_id", "region", "afk_channel_id", "afk_timeout", "widget_enabled",
                "widget_channel_id", "verification_level", "default_message_notifications", "explicit_content_filter",
                "mfa_level",
            }
        })

    async def _save_roles(self):
        self.data["roles"] = [
            r.to_dict()
            for r in self.guild.roles
            if not r.managed
        ]

    async def _save_channels(self):
        self.data["channels"] = [
            c.to_dict()
            for c in self.guild.channels
        ]

    async def _save_bans(self):
        self.data["bans"] = [
            {
                "reason": ban["reason"],
                "id": ban["user"]["id"]
            }
            for ban in await self.guild.fetch_bans()
        ]

    async def _save_members(self):
        self.data["members"] = []
        after = "0"
        while True:
            members = await self.http.get_guild_members(self.guild, limit=1000, after=after)
            if len(members) == 0:
                break

            for member in members:
                self.data["members"].append({
                    "id": member.id,
                    "name": member.name,
                    "nick": member.nick,
                    "roles": member.roles
                })
                after = member.id

    async def _save_messages(self):
        def add_author(member):
            for i, m in enumerate(self.data["members"]):
                if m["id"] == member.id:
                    break

            else:
                self.data["members"].append({
                    "id": member.id,
                    "name": member.name,
                    "nick": None,
                    "roles": []
                })

        def serialize_message(msg):
            return {
                "id": msg.id,
                "content": msg.content,
                "author": {
                    "id": msg.author.id,
                    "name": msg.author.name
                },
                "attachments": [
                    {
                        "filename": attachment.filename,
                        "url": attachment.url
                    }
                    for attachment in msg.attachments
                ],
                "pinned": msg.pinned,
                "embeds": msg.embeds
            }

        self.data["messages"] = {}
        for channel in self.guild.channels:
            if channel.type not in {ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS}:
                continue

            # TODO: save pins

            if self.chatlog == 0:
                continue

            channel_messages = self.data["messages"][channel.id] = []
            before = None
            while len(channel_messages) < self.chatlog:
                messages = await self.http.get_channel_messages(channel, limit=100, before=before)
                if len(messages) == 0:
                    break

                for message in messages:
                    # add_author(message.author)
                    channel_messages.append(serialize_message(message))
                    before = message.id

                    if len(channel_messages) >= self.chatlog:
                        break

    async def save(self, **options):
        savers = OrderedDict(
            roles=self._save_roles,
            channels=self._save_channels,
            bans=self._save_bans,
            members=self._save_members,
            messages=self._save_messages
        )

        self.guild = await self.http.get_guild(self.guild_id)
        self.guild.http = self.http
        await self.guild.fetch_channels()

        self.chatlog = options.get("chatlog", 0)

        await self._save_base()
        for name, saver in savers.items():
            if options.get(name) is not False:
                yield name, saver()


class RoleRateLimit(Exception):
    def __init__(self, ratelimit):
        self.ratelimit = ratelimit


class LoaderOptions:
    def __init__(self, default):
        self.all = False
        self.options = {}
        self.update(default)

    def update(self, options):
        for key in options.replace("-", "_").split(" "):
            value = True
            if key.startswith("!"):
                key = key[1:]
                value = False

            if key == "*":
                self.all = value
                self.options.clear()

            else:
                self.options[key] = value

    def __getattr__(self, item):
        return self.get(item)

    def get(self, item):
        if item in self.options.keys():
            return bool(self.options[item])

        return self.all


class GuildLoader:
    def __init__(self, bot, guild_id, data, options=None, ignore=None, reason="Backup loaded"):
        self.bot = bot
        self.http = bot.http
        self.guild_id = guild_id
        self.guild = None
        self.data = data

        self.reason = reason
        self.options = options or {}
        self.ignore_ids = ignore or []
        self.ids = {data["id"]: guild_id}

    async def _delete_roles(self):
        existing = [
            r for r in self.guild.roles
            if not r.managed and not r.id == self.guild_id
        ]

        for role in sorted(existing, key=lambda r: r.position):
            if role.id in self.ignore_ids:
                continue

            try:
                await self.http.delete_guild_role(self.guild, role, reason=self.reason)
            except HTTPForbidden:
                break

            except HTTPException:
                pass

    async def _load_roles(self):
        roles = list(sorted(self.data["roles"], key=lambda r: r["position"], reverse=True))
        for role in roles:
            # Default role (@everyone)
            # role["id"] == 0 is an edge case of cross-loaded templates
            if role["id"] == self.data["id"] or role["id"] == 0:
                to_edit = self.guild.default_role
                if to_edit is None:
                    continue

                self.ids[role["id"]] = to_edit.id
                try:
                    await self.http.edit_guild_role(self.guild, to_edit, **role, reason=self.reason)
                except HTTPException:
                    pass

            else:
                req = self.http.create_guild_role(self.guild, **role, reason=self.reason)
                try:
                    new = await asyncio.wait_for(req, timeout=30)

                except asyncio.TimeoutError:
                    raise RoleRateLimit(req.ratelimit)

                except HTTPException:
                    pass

                else:
                    self.ids[role["id"]] = new.id

    async def _delete_channels(self):
        for channel in self.guild.channels:
            if channel.id in self.ignore_ids:
                continue

            try:
                await self.http.delete_channel(channel, reason=self.reason)
            except HTTPException:
                pass

    async def _load_channels(self):
        def _tune_channel(channel):
            channel.pop("guild_id", None)

            # Bitrates over 96000 require special features or boosts
            # (boost advantages change a lot, so we just ignore them)
            if "bitrate" in channel.keys() and "VIP_REGIONS" not in self.guild.features:
                channel["bitrate"] = min(channel["bitrate"], 96000)

            # News and store channels require special features
            if (channel["type"] == ChannelType.GUILD_NEWS and "NEWS" not in self.guild.features) or \
                    (channel["type"] == ChannelType.GUILD_STORE and "COMMERCE" not in self.guild.features):
                channel["type"] = 0

            channel["type"] = 0 if channel["type"] > 4 else channel["type"]

            if "parent_id" in channel.keys():
                if channel["parent_id"] in self.ids:
                    channel["parent_id"] = self.ids[channel["parent_id"]]

                else:
                    del channel["parent_id"]

            overwrites = channel.get("permission_overwrites", [])
            new_overwrites = []
            for overwrite in overwrites:
                if overwrite["id"] in self.ids:
                    overwrite["id"] = self.ids[overwrite["id"]]
                    new_overwrites.append(overwrite)

            channel["permission_overwrites"] = new_overwrites[:100]

            return channel

        no_parent = sorted(
            filter(lambda c: c.get("parent_id") is None, self.data["channels"]),
            key=lambda c: c.get("position")
        )
        for channel in no_parent:
            try:
                new = await self.http.create_guild_channel(self.guild, **_tune_channel(channel), reason=self.reason)
                self.ids[channel["id"]] = new.id
            except HTTPException:
                pass

        has_parent = sorted(
            filter(lambda c: c.get("parent_id") is not None, self.data["channels"]),
            key=lambda c: c["position"]
        )
        for channel in has_parent:
            try:
                new = await self.http.create_guild_channel(self.guild, **_tune_channel(channel), reason=self.reason)
                self.ids[channel["id"]] = new.id
            except HTTPException:
                pass

    async def _load_bans(self):
        existing_bans = [b["user"]["id"] for b in await self.http.get_guild_bans(self.guild)]

        for ban in filter(lambda b: b["id"] not in existing_bans, self.data.get("bans", [])):
            try:
                await self.http.create_guild_ban(self.guild, ban["id"], reason=ban["reason"])
            except HTTPException:
                pass

    async def _load_members(self):
        pass

    async def _load_messages(self):
        pass

    async def _load_settings(self):
        await self.http.edit_guild(self.guild, **{
            k: self.ids.get(v, v)
            for k, v in self.data.items()
            if type(v) == str
        })

    async def load(self):
        loaders = OrderedDict(
            delete_roles=self._delete_roles,
            roles=self._load_roles,
            delete_channels=self._delete_channels,
            channels=self._load_channels,
            settings=self._load_settings,
            bans=self._load_bans,
            members=self._load_members,
            messages=self._load_messages
        )

        self.guild = await self.http.get_guild(self.guild_id)
        self.guild.http = self.http
        await self.guild.fetch_channels()

        for name, loader in loaders.items():
            if self.options.get(name):
                yield name, loader()


async def run_loader(loader):
    bot = loader.bot
    loop = bot.loop
    redis_key = f"cmd:loaders:{loader.guild_id}"

    async for option, coro in loader.load():
        yield option
        task = loop.create_task(coro)
        while not task.done():
            await bot.redis.setex(redis_key, 10, option)
            await asyncio.sleep(5)

        try:
            task.result()
        except:
            traceback.print_exc()


option_text = OrderedDict(
    delete_roles="Deleting existing roles",
    roles="Loading roles",
    delete_channels="Deleting existing channels",
    channels="Loading channels",
    settings="Loading server settings",
    bans="Loading banned users",
    members="Loading member roles and nicknames",
    messages="Loading messages"
)


def warning_text(options):
    result = "**Are you sure that you want to load this backup or template?**\n\n" \
             "__Planned Actions__\n\n"

    for opt, text in option_text.items():
        if options.get(opt):
            result += f"- {text}\n"

    result += "\n*Please put the managed bot role above all other roles that you want to replace " \
              f"before clicking the ✅ reaction.*\n\n"
    result += "*Also keep in mind that you can only load up to 250 roles per 48 hours.*"
    return result


def status_text(options, option):
    result = ""
    for opt, text in option_text.items():
        if not options.get(opt):
            continue

        if opt == option:
            result += f"- **{text}**\n"

        else:
            result += f"- {text}\n"

    result += "\n*Please be patient, this could take a while.*"
    return result
