from enum import IntEnum
from uuid import uuid4


__all__ = (
    "ComponentType",
    "Component",
    "ActionRow",
    "ButtonStyle",
    "Button"
)


class ComponentType(IntEnum):
    ACTION_ROW = 1
    BUTTON = 2


class Component:
    def __init__(self, **kwargs):
        self.type = ComponentType(kwargs["type"])

    def to_payload(self):
        return {
            "type": self.type.value
        }


class ActionRow(Component):
    def __init__(self, *components):
        super().__init__(type=ComponentType.ACTION_ROW)
        self.components = list(components)

    def to_payload(self):
        return {
            "type": self.type.value,
            "components": [c.to_payload() for c in self.components]
        }


class ButtonStyle(IntEnum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4


class Button(Component):
    def __init__(self, **kwargs):
        super().__init__(type=ComponentType.BUTTON)
        self.label = kwargs["label"]
        self.custom_id = kwargs.get("custom_id", uuid4().hex)
        self.style = ButtonStyle(kwargs.get("style", ButtonStyle.PRIMARY))
        self.url = kwargs.get("url")
        self.emoji = kwargs.get("emoji")
        self.disabled = kwargs.get("disabled", False)

    def to_payload(self):
        return {
            "type": self.type.value,
            "label": self.label,
            "custom_id": self.custom_id,
            "style": self.style.value,
            "url": self.url,
            "emoji": self.emoji,
            "disabled": self.disabled
        }
