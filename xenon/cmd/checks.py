import dc_interactions as dc
from enum import IntEnum
from xenon import *

from .formatter import *


__all__ = (
    "has_permissions",
    "bot_has_permissions",
    "is_bot_owner",
    "is_guild_owner",
    "has_permissions_level",
    "PermissionLevels"
)


def has_permissions(*args, **kwargs):
    @dc.Check
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
            embed=False,
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return _check


def bot_has_permissions(*args, **kwargs):
    @dc.Check
    async def _check(ctx, **_):
        required = list(args) + list(kwargs.keys())
        bot_member = await ctx.fetch_bot_member()
        guild = await ctx.fetch_guild()

        if bot_member.id == guild.owner_id:
            return True

        perms = Permissions.none()
        roles = sorted(guild.roles, key=lambda r: r.position)
        for role in roles:
            if role.id in bot_member.roles:
                perms.value |= role.permissions.value

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
            embed=False,
            f=Format.ERROR
        ), ephemeral=True)
        return False

    return _check


@dc.Check
async def is_guild_owner(ctx, *args, **kwargs):
    guild = await ctx.fetch_guild()
    if ctx.author.id != guild.owner_id:
        await ctx.respond(**create_message(
            "Only the **server owner** can use this command.\n",
            embed=False,
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
                    embed=False,
                    f=Format.ERROR
                ), ephemeral=True)
                return False

            else:
                return await has_permissions("administrator")(callback).run(ctx, **kwargs)

        return dc.Check(_check, callback)

    return predicate


@dc.Check
async def is_bot_owner(ctx, **_):
    app = await ctx.bot.http.get_app_info()
    if ctx.author.id != app["owner"]["id"]:
        team = app.get("team")
        if team is not None:
            members = [tm["user"]["id"] for tm in team["members"]]
            if ctx.author.id in members:
                return True

        await ctx.respond(**create_message(
            "This command can **only** be used by the **bot owner(s)**.",
            embed=False,
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

    @dc.Check
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
                f"You have to **wait `{remaining}` seconds** until you can use it again.",
                embed=False,
                f=Format.ERROR
            ), ephemeral=True)
            return False

        if not manual:
            await count()

        return True

    return _check