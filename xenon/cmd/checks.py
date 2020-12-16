from enum import IntEnum

from .errors import *

__all__ = (
    "Check",
    "CheckFailed",
    "is_bot_owner",
    "has_permissions",
    "bot_has_permissions",
    "Cooldown",
    "OnCooldown",
    "cooldown"
)


class Check:
    def __init__(self, check, next_):
        self.check = check
        self.next = next_

    def run(self, ctx, *args):
        return self.check(ctx, *args)


def is_bot_owner(next_):
    async def check(ctx, *args):
        guild = await ctx.get_guild()
        if guild.owner_id == ctx.author.id:
            return True

        raise NotGuildOwner()

    return Check(check, next_)


def has_permissions(*perms):
    def predicate(next_):
        async def check(ctx, *args):
            if ctx.member.permissions.administrator:
                # administrator bypasses all
                return True

            missing = set()
            for perm in perms:
                if not getattr(ctx.member.permissions, perm):
                    missing.add(perm)

            if len(missing) > 0:
                raise PermissionError(missing)

            return True

        return Check(check, next_)

    return predicate


def bot_has_permissions(*perms):
    def predicate(next_):
        async def check(ctx, *args):
            # TODO: Get actual bot member lol
            if ctx.member.permissions.administrator:
                # administrator bypasses all
                return True

            missing = set()
            for perm in perms:
                if not getattr(ctx.member.permissions, perm):
                    missing.add(perm)

            if len(missing) > 0:
                raise BotMissingPermissions(missing)

            return True

        return Check(check, next_)

    return predicate


class CooldownType(IntEnum):
    GLOBAL = 0
    GUILD = 1
    CHANNEL = 2
    AUTHOR = 3


class Cooldown(Check):
    def __init__(self, next_, rate: int, per: float, bucket=CooldownType.AUTHOR):
        super().__init__(self.check, next_)
        self.rate = rate
        self.per = per
        self.bucket = bucket

    async def check(self, ctx, *args):
        pass

    async def reset(self, ctx):
        pass


def cooldown(*args, **kwargs):
    def predicate(next_):
        return Cooldown(next_, *args, **kwargs)

    return predicate
