from enum import IntEnum


__all__ = (
    "InteractionResponseType",
    "InteractionResponse"
)


class InteractionResponseType(IntEnum):
    PONG = 1
    CHANNEL_MESSAGE = 4
    DEFERRED = 5


class InteractionResponse:
    def __init__(self, type, content=None, **kwargs):
        self.type = type
        self.files = kwargs.pop("files", [])
        self.data = kwargs
        if "allowed_mentions" not in self.data:
            self.data["allowed_mentions"] = {"parse": ["users"]}

        self.data["content"] = content
        if kwargs.pop("ephemeral", False):
            self.data["flags"] = 1 << 6

    @classmethod
    def pong(cls):
        return cls(InteractionResponseType.PONG)

    @classmethod
    def defer(cls, *args, **kwargs):
        return cls(InteractionResponseType.DEFERRED, *args, **kwargs)

    @classmethod
    def message(cls, content=None, **kwargs):
        return cls(InteractionResponseType.CHANNEL_MESSAGE, content=content, **kwargs)

    def to_dict(self):
        return {
            "type": self.type.value,
            "data": self.data
        }
