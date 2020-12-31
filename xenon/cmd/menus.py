import asyncio

from ..entities import *
from .formatter import *


__all__ = (
    "reaction_confirmation",
    "ListMenu"
)


async def reaction_confirmation(bot, msg, user_id):
    msg.http = bot.http
    emojis = ("✅", "❌")

    async def add_reactions():
        for emoji in emojis:
            await msg.create_reaction(emoji)

    def check(reaction):
        if reaction["message_id"] != msg.id:
            return False

        if reaction["user_id"] != user_id:
            return False

        if reaction["emoji"]["name"] not in emojis:
            return False

        return True

    bot.loop.create_task(add_reactions())
    try:
        reaction = await bot.wait_for("message_reaction_add", check=check, timeout=30)
    except asyncio.TimeoutError:
        await msg.delete_all_reactions()
        return False

    await msg.delete_all_reactions()
    if reaction["emoji"]["name"] == emojis[0]:
        return True

    return False


class ListMenu:
    embed_kwargs = {}
    per_page = 10

    def __init__(self, ctx, msg=None):
        self.ctx = ctx
        self.msg = msg
        self.page = 0

    async def get_items(self):
        return []

    async def update(self):
        items = await self.get_items()
        if len(items) == 0 and self.page > 0:
            self.page -= 1
            await self.update()
            return

        if self.msg is None:
            self.msg = Message(await self.ctx.respond(embeds=self.make_embeds(items)))

        else:
            await self.ctx.edit_response(embeds=self.make_embeds(items), message_id=self.msg.id)

        if len(items) < self.per_page and self.page == 0:
            # If the first page doesn't contain any backups, there is no need to keep up the pagination
            raise asyncio.CancelledError()

    def make_embeds(self, items):
        if len(items) > 0:
            return [{
                "title": "List",
                "color": Format.INFO.color,
                "fields": [
                    {
                        "name": name,
                        "value": value,
                        "inline": False
                    }
                    for name, value in items
                ],
                "footer": {
                    "text": f"Page {self.page + 1}"
                },
                **self.embed_kwargs
            }]

        else:
            return [{
                "title": "List",
                "color": Format.INFO.color,
                "description": "Nothing to display",
                **self.embed_kwargs
            }]

    async def start(self):
        await self.update()
        self.msg.http = self.ctx.bot.http
        options = ["◀", "❎", "▶"]
        for option in options:
            await self.msg.create_reaction(option)

        def check(reaction):
            if reaction["message_id"] != self.msg.id:
                return False

            if reaction["user_id"] != self.ctx.author.id:
                return False

            if reaction["emoji"]["name"] not in options:
                return False

            return True

        try:
            while True:
                try:
                    data = await self.ctx.bot.wait_for(
                        "message_reaction_add",
                        check=check,
                        timeout=30,
                    )

                    emoji = data["emoji"]["name"]
                    try:
                        await self.msg.delete_user_reaction(emoji, data["user_id"])
                    except Exception:
                        pass

                    if str(emoji) == options[0]:
                        if self.page > 0:
                            self.page -= 1

                    elif str(emoji) == options[2]:
                        self.page += 1

                    else:
                        raise asyncio.CancelledError()

                    await self.update()

                except asyncio.TimeoutError:
                    return

        finally:
            try:
                await self.msg.delete_all_reactions()
            except Exception:
                pass
