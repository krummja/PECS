from __future__ import annotations
from beartype.typing import Any

from deepmerge import always_merger

from pecs_framework.entity import Entity, add_component_type
from pecs_framework.component import Component


class PrefabComponent:

    def __init__(
            self, 
            cls: Component, 
            properties: dict[str, Any], 
            overwrite: bool = True,
        ) -> None:
        self.component = cls
        self.properties = properties if properties else {}
        self.overwrite = overwrite

    def apply(self, entity: Entity, initial_props: dict[str, Any] = None) -> None:
        if not initial_props:
            initial_props = {}

        props = always_merger.merge(self.properties, initial_props)
        add_component_type(entity, self.component, props)


class PrefabEntity:

    def __init__(
            self,
            name: str,
            inherit: list[PrefabComponent] = None,
            components: list[PrefabComponent] = None,
        ) -> None:
        self.name = name
        self.inherit = inherit if inherit else []
        self.components = components if components else []
