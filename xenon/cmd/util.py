import asyncio
import traceback

__all__ = (
    "list_get",
    "require_confirmation",
    "ListMenu"
)


def list_get(iterable, **keys):
    for thing in iterable:
        for key, value in keys.items():
            if getattr(thing, key) != value:
                break

        else:
            return thing


async def require_confirmation(ctx, msg):
    msg.fill_http(ctx.bot.http)

    reactions = ("✅", "❌")
    for reaction in reactions:
        await msg.create_reaction(reaction)

    try:
        reaction = await ctx.bot.wait_for(
            "message_reaction_add",
            check=lambda d: d["message_id"] == msg.id
                            and d["user_id"] == ctx.author.id
                            and d["emoji"]["name"] in reactions,
            timeout=30
        )
    except asyncio.TimeoutError:
        await msg.delete_all_reactions()
        return False

    if reaction["emoji"]["name"] == reactions[1]:
        await msg.delete_all_reactions()
        return False

    await msg.delete_all_reactions()
    return True


class ListMenu:
    embed_kwargs = {}
    empty_text = "Nothing to display"

    def __init__(self, ctx, msg):
        self.ctx = ctx
        self.msg = msg
        self.msg.fill_http(ctx.bot.http)
        self.page = 0

    async def get_items(self):
        return []

    async def update(self):
        items = await self.get_items()
        if len(items) == 0 and self.page > 0:
            self.page -= 1
            await self.update()
            return

        await self.ctx.edit_response("", embeds=self.make_embeds(items), message_id=self.msg.id)

        if len(items) == 0 and self.page == 0:
            # If the first page doesn't contain any backups, there is no need to keep up the pagination
            raise asyncio.CancelledError()

    def make_embeds(self, items):
        if len(items) > 0:
            return [{
                "title": "List",
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
                "description": self.empty_text,
                **self.embed_kwargs
            }]

    async def start(self):
        await self.update()
        options = ["◀", "❎", "▶"]
        for option in options:
            await self.msg.create_reaction(option)

        try:
            while True:
                try:
                    data = await self.ctx.bot.wait_for(
                        "message_reaction_add",
                        check=lambda d: d["user_id"] == self.ctx.author.id and
                                        d["message_id"] == self.msg.id and
                                        d["emoji"]["name"] in options,
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
