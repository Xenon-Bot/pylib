from enum import IntEnum


__all__ = (
    "InteractionType",
    "InteractionResponseType",
    "CommandOptionType"
)


class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2


class InteractionResponseType(IntEnum):
    PONG = 1
    ACKNOWLEDGE = 2
    CHANNEL_MESSAGE = 3
    CHANNEL_MESSAGE_WITH_SOURCE = 4


class CommandOptionType(IntEnum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
