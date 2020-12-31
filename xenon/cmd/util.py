from datetime import datetime, timedelta
import re

from ..enums import *


__all__ = (
    "datetime_to_string",
    "timedelta_to_string",
    "string_to_timedelta",
    "time_units",
    "channel_tree"
)


def datetime_to_string(dt: datetime):
    return dt.strftime("%d. %b %Y - %H:%M")


time_units = (
    (("w", "week", "weeks"), 7 * 24 * 60 * 60),
    (("d", "day", "days"), 24 * 60 * 60),
    (("h", "hour", "hours"), 60 * 60),
    (("m", "min", "minute", "minutes"), 60),
    (("s", "second", "seconds"), 1)
)


def timedelta_to_string(td: timedelta, precision="s"):
    seconds = td.total_seconds()
    if seconds == 0:
        return "0 seconds"

    result = ""
    for names, mp in time_units:
        count, seconds = divmod(seconds, mp)
        count = int(count)
        if count > 0:
            result += f" {count} {names[-2] if count == 1 else names[-1]}"

        if precision in names:
            break

    return result.strip()


def string_to_timedelta(string):
    def get_multiplier(name):
        for names, mp in time_units:
            if name in names:
                return mp

        return ValueError

    parts = string.split(" ")
    seconds = 0
    i = 0
    while i < len(parts):
        part = parts[i]
        if re.match(r"^[0-9]+$", part):
            try:
                count = int(part)
                unit = parts[i + 1]
                mp = get_multiplier(unit)
                seconds += count * mp
            except (ValueError, IndexError):
                i += 1
            else:
                i += 2

        else:
            try:
                count, unit = int(part[:-1]), part[-1]
                mp = get_multiplier(unit)
                seconds += count * mp
            except (ValueError, IndexError):
                pass
            finally:
                i += 1

    return timedelta(seconds=seconds)


def channel_tree(channels):
    text = []
    voice = []
    ctg = []

    for channel in sorted(channels, key=lambda c: c.position):
        if channel.type == ChannelType.GUILD_VOICE:
            voice.append(channel)

        elif channel.type == ChannelType.GUILD_CATEGORY:
            ctg.append(channel)

        else:
            text.append(channel)

    result = "```"
    text_no_ctg = filter(lambda t: t.parent_id is None, text)
    for channel in text_no_ctg:
        result += "\n#\u200a" + channel.name

    voice_no_ctg = filter(lambda v: v.parent_id is None, voice)
    for channel in voice_no_ctg:
        result += "\n<\u200a" + channel.name

    result += "\n"

    for category in ctg:
        result += "\n°\u200a" + category.name
        t_children = filter(lambda c: c.parent_id == category.id, text)
        for channel in t_children:
            result += "\n  #\u200a" + channel.name

        v_children = filter(lambda c: c.parent_id == category.id, voice)
        for channel in v_children:
            result += "\n  <\u200a" + channel.name

        result += "\n"

    return result + "```"
