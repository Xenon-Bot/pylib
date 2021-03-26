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
        if kwargs.get("ephemeral"):
            self.data["flags"] = 1 << 6

    @classmethod
    def pong(cls):
        return cls(InteractionResponseType.PONG)

    @classmethod
    def defer(cls):
        return cls(InteractionResponseType.DEFERRED)

    @classmethod
    def message(cls, content=None, **kwargs):
        return cls(InteractionResponseType.CHANNEL_MESSAGE, content=content, **kwargs)

    def to_dict(self):
        if self.type == InteractionResponseType.DEFERRED:
            return {"type": self.type.value}

        return {
            "type": self.type.value,
            "data": self.data
        }
