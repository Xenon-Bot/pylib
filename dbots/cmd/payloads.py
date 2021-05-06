from enum import IntEnum

from .. import Member, User, Role, Channel, Message, Snowflake
from .components import ComponentType


__all__ = (
    "InteractionType",
    "InteractionPayload",
    "CommandInteractionData",
    "CommandInteractionDataOption",
    "ComponentInteractionData"
)


class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    APPLICATION_COMPONENT = 3


class ResolvedEntities:
    def __init__(self, data):
        users = data.get("users", {})
        self.users = {k: User(v) for k, v in users.items()}
        self.members = {}
        for id, member in data.get("members", {}).items():
            user = users.get(id)
            if user is not None:
                self.members[id] = Member({"user": user, **member})

        self.roles = {k: Role(v) for k, v in data.get("roles", {}).items()}
        self.channels = {k: Channel(v) for k, v in data.get("channels", {}).items()}


class InteractionPayload:
    def __init__(self, data):
        self.id = data["id"]
        self.type = InteractionType(data["type"])
        self.guild_id = data.get("guild_id")
        self.channel_id = data.get("channel_id")
        self.token = data.get("token")
        self.version = data.get("version")

        if self.type != InteractionType.PING:
            if "member" in data:
                self.author = Member(data["member"])
            else:
                self.author = User(data["user"])

        if self.type == InteractionType.APPLICATION_COMMAND:
            self.data = CommandInteractionData(data["data"])

        elif self.type == InteractionType.APPLICATION_COMPONENT:
            if data["message"].get("flags") == 64:
                self.message = Snowflake(data["message"]["id"])
            else:
                self.message = Message(data["message"])

            self.data = ComponentInteractionData(data["data"])


class CommandInteractionData:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.resolved = ResolvedEntities(data.get("resolved", {}))
        self.options = [CommandInteractionDataOption(o) for o in data.get("options", [])]


class CommandInteractionDataOption:
    def __init__(self, data):
        self.name = data["name"]
        self.value = data.get("value")
        self.options = [CommandInteractionDataOption(o) for o in data.get("options", [])]


class ComponentInteractionData:
    def __init__(self, data):
        self.custom_id = data["custom_id"]
        self.component_type = ComponentType(data["component_type"])
