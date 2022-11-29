from __future__ import annotations
from beartype.typing import Any, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from pecs_framework.domain import Domain
    from pecs_framework.engine import Engine

from deepmerge import always_merger
import json

from pecs_framework.entity import Entity, add_component_type
from pecs_framework.component import Component, ComponentMeta


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
        self.domain = engine.domain
        self._templates: dict[str, EntityTemplate] = {}

    def deserialize(self, definition: str) -> EntityTemplate:
        data = dict(json.loads(definition))

        # Unpack component definitions and set up templates.
        component_templates = []
        
        for comp_def in data["components"]:
            component_templates.append({
                "component_type"    : comp_def["type"],
                "properties"        : comp_def.get("properties", {}),
            })

        return {
            "name"          : data["name"],
            "inherit"       : data.get("inherit", []),
            "components"    : component_templates,
        }

    def register(self) -> None:
        pass

    def create(
            self,
            template_name: str, 
            properties: dict[str, Any],
            entity_uid: str | None = None,
        ) -> Entity:
        entity = self.domain.entities.create(entity_uid)

        return entity
