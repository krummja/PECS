from __future__ import annotations
from beartype.typing import Any, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from pecs_framework.domain import Domain
    from pecs_framework.engine import Engine

from deepmerge import always_merger
import json

from pecs_framework.entity import Entity, add_component_type
from pecs_framework.component import Component, ComponentMeta


# In order to create a prefab, I need to basically automate the process of building
# out an entity and its component structure based on a TOML or JSON definition.

# A Prefab is basically just an Entity with attached Components, preconfigured and
# able to be copied or used as a template for generating new concrete Entity instances.

"""
{
    "name": "GameObject",
    "inherit": [],
    "components": [
        {
            "type": "Position",
        },
        {
            "type": "Renderable",
            "properties": {
                "char": "?"
            }
        },
        {
            "type": "Noun",
            "properties": {
                "text": "<unset>"
            }
        }
    ]
}
"""

class ComponentTemplate(TypedDict):
    component_type: str
    properties: dict[str, Any]


class EntityTemplate(TypedDict):
    name: str
    inherit: list[str]
    components: list[ComponentTemplate]


class PrefabBuilder:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._templates: dict[str, EntityTemplate] = {}

    def deserialize(self, definition: str) -> EntityTemplate:
        data = dict(json.loads(definition))

        print(data)

        # Unpack component definitions and set up templates.
        component_templates = []
        for definition in data["components"]:
            component_templates.append({
                "component_type": definition["type"],
                "properties": definition.get("properties", {}),
            })

        return {
            "name": data["name"],
            "inherit": data.get("inherit", []),
            "components": component_templates,
        }
