import inspect
from enum import IntEnum

from .formatter import *

__all__ = (
    "Check",
    "has_permissions",
    "bot_has_permissions",
    "is_bot_owner",
    "is_guild_owner",
    "has_permissions_level",
    "PermissionLevels",
    "not_in_maintenance",
    "guild_only",
    "dm_only",
    "cooldown"
)


class Check:
    def __init__(self, callable, next=None):
        self.callable = callable
        self.next = next

    def __call__(self, next):
        self.next = next
        return self

    async def run(self, ctx, **kwargs):
        result = self.callable(ctx, **kwargs)
        if inspect.isawaitable(result):
            result = await result

        return result


def has_permissions(*args, **kwargs):
    @Check
    async def _check(ctx, **_):
        required = list(args) + list(kwargs.keys())
        perms = ctx.author.permissions

        if perms.administrator:
            return True

        missing = []
        for perm in required:
            if not getattr(perms, perm, False):
                missing.append(perm.title())

        if len(missing) == 0:
            return True

        await ctx.respond(**create_message(
            f"**You are missing** the following **permissions**: `{', '.join(missing)}`.",
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return _check


def bot_has_permissions(*args, **kwargs):
    @Check
    async def _check(ctx, **_):
        required = list(args) + list(kwargs.keys())
        bot_member = await ctx.fetch_bot_member()
        guild = await ctx.fetch_guild()

        perms = guild.compute_permissions(bot_member)
        if perms.administrator:
            return True

        missing = []
        for perm in required:
            if not getattr(perms, perm, False):
                missing.append(perm.title())

        if len(missing) == 0:
            return True

        await ctx.respond(**create_message(
            f"**The bot is missing** the following **permissions**: `{', '.join(missing)}`.",
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return _check


@Check
async def is_guild_owner(ctx, *args, **kwargs):
    guild = await ctx.fetch_guild()
    if ctx.author.id != guild.owner_id:
        await ctx.respond(**create_message(
            "Only the **server owner** can use this command.\n",
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return True


class PermissionLevels(IntEnum):
    ADMIN_ONLY = 0
    DESTRUCTIVE_OWNER = 1
    OWNER_ONLY = 2


def has_permissions_level(destructive=False):
    def predicate(callback):
        async def _check(ctx, **kwargs):
            settings = await ctx.bot.db.guilds.find_one({"_id": ctx.guild_id})
            if settings is None or "permissions_level" not in settings:
                required = PermissionLevels.DESTRUCTIVE_OWNER

            else:
                required = PermissionLevels(settings["permissions_level"])

            if required == PermissionLevels.OWNER_ONLY or \
                    (required == PermissionLevels.DESTRUCTIVE_OWNER and destructive):
                guild = await ctx.fetch_guild()
                if guild.owner_id == ctx.author.id:
                    return True

                await ctx.respond(**create_message(
                    "Only the **server owner** can use this command.\n"
                    f"The server owner can change this using "
                    f"`/help settings permissions`.",
                    f=Format.ERROR
                ), ephemeral=True)
                return False

            else:
                return await has_permissions("administrator")(callback).run(ctx, **kwargs)

        return Check(_check, callback)

    return predicate


@Check
async def is_bot_owner(ctx, **_):
    app = await ctx.bot.http.get_application()
    if ctx.author.id != app["owner"]["id"]:
        team = app.get("team")
        if team is not None:
            members = [tm["user"]["id"] for tm in team["members"]]
            if ctx.author.id in members:
                return True

        await ctx.respond(**create_message(
            "This command can **only** be used by the **bot owner(s)**.",
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return True


class CooldownType(IntEnum):
    GLOBAL = 0
    GUILD = 1
    CHANNEL = 2
    AUTHOR = 3


def cooldown(rate: int, per: int, bucket=CooldownType.AUTHOR, manual=False):
    def get_key(ctx):
        if bucket == CooldownType.GUILD:
            if ctx.guild_id is not None:
                key = ctx.guild_id

            else:
                key = ctx.channel_id

        elif bucket == CooldownType.CHANNEL:
            key = ctx.channel_id

        elif bucket == CooldownType.AUTHOR:
            key = ctx.author.id

        else:
            key = "*"

        return "cmd:cooldown:" + ctx.command.full_name.replace(" ", "") + ":" + key

    @Check
    async def _check(ctx, **_):
        key = get_key(ctx)
        current = int(await ctx.bot.redis.get(key) or 0)

        async def reset(*_):
            key = get_key(ctx)
            await ctx.bot.redis.delete(key)

        async def count(*_):
            await ctx.bot.redis.setex(key, per, current + 1)

        ctx.reset_cooldown = reset
        ctx.count_cooldown = count

        if current >= rate:
            remaining = await ctx.bot.redis.ttl(key)
            await ctx.respond(**create_message(
                f"This **command** is currently on **cooldown**.\n"
                f"You have to **wait `{remaining}` second(s)** until you can use it again.",
                f=Format.ERROR
            ), ephemeral=True)
            return False

        if not manual:
            await count()

        return True

    return _check


@Check
async def not_in_maintenance(ctx, **_):
    in_maintenance = await ctx.bot.redis.exists("cmd:maintenance")
    if in_maintenance:
        await ctx.respond(**create_message(
            "The bot is currently in **maintenance**. This command can not be used during maintenance,"
            " please be patient and **try again in a few minutes**.",
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return True


@Check
async def guild_only(ctx, **_):
    if ctx.guild_id is None:
        await ctx.respond(**create_message(
            "This command can **only** be used **inside a server**.",
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return True


@Check
async def dm_only(ctx, **_):
    if ctx.guild_id is not None:
        await ctx.respond(**create_message(
            "This command can **only** be used inside **direct messages**.",
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return True
