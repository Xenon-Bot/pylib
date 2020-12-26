import re


__all__ = (
    "Format",
    "FormatValue",
    "create_message"
)


class FormatValue:
    def __init__(self, title=None, color=None, emoji=None):
        self.title = title
        self.color = color
        self.emoji = emoji


class Format:
    DEFAULT = FormatValue()
    INFO = FormatValue(
        title="Info",
        color=0x478fce,
        emoji="<:info:777557308258517032>"
    )
    SUCCESS = FormatValue(
        title="Success",
        color=0x48ce6c,
        emoji="<:success:777557308447391775>"
    )
    WARNING = FormatValue(
        title="Warning",
        color=0xefbc2f,
        emoji="<:warning:777557308439265350>"
    )
    ERROR = FormatValue(
        title="Error",
        color=0xc64935,
        emoji="<:error:777557308216967188>"
    )
    PLEASE_WAIT = FormatValue(
        title="Please Wait",
        color=0x36393e,
        emoji="<a:working:777557383693729802>"
    )


def create_message(text, f=Format.DEFAULT, embed=True):
    if embed:
        match = re.match(r"<(a?):\w+:([0-9]+)>", f.emoji)
        emoji_format = "png" if not match[1] else "gif"
        return {
            "embeds": [{
                "author": {
                    "name": f.title,
                    "icon_url": f"https://cdn.discordapp.com/emojis/{match[2]}.{emoji_format}"
                },
                "color": f.color,
                "description": text
            }]
        }

    else:
        return {
            "content": f"{f.emoji} **{f.title}**\n\n{text}"
        }
