from ..errors import XenonException

__all__ = (
    "CommandError",
    "CheckFailed",
    "MissingPermissions",
    "BotMissingPermissions",
    "NotGuildOwner",
    "ConverterFailed",
    "OnCooldown"
)


class CommandError(XenonException):
    pass


class CheckFailed(CommandError):
    pass


class MissingPermissions(CheckFailed):
    def __init__(self, missing):
        self.missing = set(missing)


class BotMissingPermissions(CheckFailed):
    def __init__(self, missing):
        self.missing = set(missing)


class NotGuildOwner(CheckFailed):
    pass


class OnCooldown(CheckFailed):
    def __init__(self, cooldown, remaining):
        self.cooldown = cooldown
        self.remaining = remaining


class ConverterFailed(CommandError):
    def __init__(self, converter):
        self.converter = converter
