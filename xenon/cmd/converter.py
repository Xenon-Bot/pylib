from .enums import *

from .errors import *


__all__ = (
    "Converter",
    "RoleConverter",
    "UserConverter",
    "ChannelConverter",
    "ConverterFailed"
)


class ConverterFailed(CommandError):
    pass


class Converter:
    type: CommandOptionType

    def __init__(self, value):
        self.value = value

    async def convert(self, ctx):
        pass


class RoleConverter(Converter):
    type = CommandOptionType.ROLE


class UserConverter(Converter):
    type = CommandOptionType.USER


class ChannelConverter(Converter):
    type = CommandOptionType.CHANNEL
