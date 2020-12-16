from enum import IntEnum


__all__ = (
    "FormatAs",
    "format_message"
)


class FormatAs(IntEnum):
    TEXT = 0
    INFO = 1
    SUCCESS = 2
    ERROR = 3
    WORKING = 4
    WARNING = 5

    EMBED = 10
    EMBED_INFO = 11
    EMBED_SUCCESS = 12
    EMBED_ERROR = 13
    EMBED_WORKING = 14
    EMBED_WARNING = 15


def format_message(text, f=FormatAs.TEXT) -> dict:
    if f == FormatAs.INFO:
        return {"content": f"<:info:777557308258517032> {text}"}

    elif f == FormatAs.SUCCESS:
        return {"content": f"<:success:777557308447391775> {text}"}

    elif f == FormatAs.ERROR:
        return {"content": f"<:error:777557308216967188> {text}"}

    elif f == FormatAs.WORKING:
        return {"content": f"<a:working:777557383693729802> {text}"}

    elif f == FormatAs.WARNING:
        return {"content": f"<:warning:777557308439265350> {text}"}

    else:
        return {"content": text}
