from ..entities import *
from .enums import *

__all__ = (
    "InteractionData",
    "CommandInteractionData",
    "CommandInteractionDataOption",
    "InteractionResponse"
)


class InteractionData(Entity):
    __slots__ = ("type", "guild_id", "channel_id", "member", "token", "data")

    def __init__(self, data):
        super().__init__()
        self.id = data["id"]
        self.type = InteractionType(data["type"])
        self.token = data["token"]
        self.guild_id = data.get("guild_id")
        self.channel_id = data.get("channel_id")
        self.member = Member(data["member"]) if "member" in data else None

        self.data = None
        if self.type == InteractionType.APPLICATION_COMMAND:
            self.data = CommandInteractionData(data["data"])

    def __iter__(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "member": dict(self.member),
            "token": self.token,
            "data": dict(self.data) if self.data is not None else None
        }


class CommandInteractionData(Entity):
    __slots__ = ("name", "options")

    def __init__(self, data):
        super().__init__()
        self.id = data["id"]
        self.name = data["name"]
        self.options = [
            CommandInteractionDataOption(o)
            for o in data.get("options", [])
        ]

    def __iter__(self):
        yield from {
            "id": self.id,
            "name": self.name,
            "options": [dict(o) for o in self.options]
        }


class CommandInteractionDataOption:
    __slots__ = ("name", "value", "options")

    def __init__(self, data):
        self.name = data["name"]
        self.value = data.get("value")
        self.options = [
            CommandInteractionDataOption(o)
            for o in data.get("options", [])
        ]

    def __iter__(self):
        yield from {
            "name": self.name,
            "value": self.value,
            "options": [dict(o) for o in self.options]
        }


class InteractionResponse:
    def __init__(self, type, data=None):
        self.type = type

        if data is not None:
            ephemeral = data.pop("ephemeral", False)
            data["flags"] = 0 if not ephemeral else 1 << 6

        self.data = data

    @classmethod
    def pong(cls):
        return cls(InteractionResponseType.PONG)

    @classmethod
    def ack(cls):
        return cls(InteractionResponseType.ACKNOWLEDGE)

    @classmethod
    def respond_and_eat(cls, **data):
        return cls(InteractionResponseType.CHANNEL_MESSAGE, data)

    @classmethod
    def respond(cls, **data):
        return cls(InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE, data)

    def __iter__(self):
        yield "type", self.type.value
        yield "data", self.data
