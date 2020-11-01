from entities import *
from .enums import *


__all__ = (
    "InteractionData",
    "CommandInteractionData",
    "CommandInteractionDataOption",
    "Command",
    "CommandOption",
    "CommandOptionChoice"
)


class InteractionData(Entity):
    __slots__ = ("type", "guild_id", "channel_id", "member", "token", "data")

    def __init__(self, data):
        super().__init__()
        self.id = data["id"]
        self.type = InteractionType(data["type"])
        self.guild_id = data["guild_id"]
        self.channel_id = data["channel_id"]
        self.member = Member(data["member"])
        self.token = data["token"]

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
        self.options = data["options"]

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
            CommandInteractionData(d)
            for d in data.get("options", [])
        ]

    def __iter__(self):
        yield from {
            "name": self.name,
            "value": self.value,
            "options": [dict(o) for o in self.options]
        }


class Command(Entity):
    __slots__ = ("application_id", "name", "description", "options")

    def __init__(self, data):
        super().__init__()
        self.id = data["id"]
        self.application_id = data["application_id"]
        self.name = data["name"]
        self.description = data["description"]
        self.options = [CommandOption(o) for o in data["options"]]

    def __iter__(self):
        yield from {
            "id": self.id,
            "application_id": self.application_id,
            "name": self.name,
            "description": self.description,
            "options": [dict(o) for o in self.options]
        }


class CommandOption:
    __slots__ = ("type", "name", "description", "default", "required", "choices", "options")

    def __init__(self, data):
        self.type = CommandOptionType(data["type"])
        self.name = data["name"]
        self.description = data["description"]
        self.default = data["default"]
        self.required = data["required"]
        self.choices = [CommandOptionChoice(c) for c in data["choices"]]
        self.options = [CommandOption(o) for o in data.get("options", [])]

    def __iter__(self):
        yield from {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "default": self.default,
            "required": self.required,
            "choices": [dict(c) for c in self.choices],
            "options": [dict(o) for o in self.options]
        }


class CommandOptionChoice:
    __slots__ = ("name", "value")

    def __init__(self, data):
        self.name = data["name"]
        self.value = data["value"]

    def __iter__(self):
        yield from {
            "name": self.name,
            "value": self.value
        }
