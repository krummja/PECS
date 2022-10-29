from __future__ import annotations
from typing import *

from pecs_framework.entity import Entity
from pecs_framework.prefab_component import PrefabComponent


class PrefabEntity:

    def __init__(
            self,
            name: str,
            inherit: list[PrefabEntity] | None = None,
            components: list[PrefabComponent] | None = None,
        ) -> None:
        self.name = name
        self.inherit = inherit or []
        self.prefab_components = components or []

    def add_component(self, component: PrefabComponent) -> None:
        self.prefab_components.append(component)

    def apply_to_entity(
            self,
            entity: Entity,
            prefab_props: Optional[Dict[str, Any]] = None
        ) -> Entity:
        prefab_props = prefab_props or {}
        properties = {k.upper(): v for k, v in prefab_props.items()}

        for parent in self.inherit:
            parent.apply_to_entity(entity, properties)

        arr_comps = {}

        for prefab_component in self.prefab_components:
            klass = prefab_component.klass
            initial_props = {}

            if klass.allow_multiple:
                if not arr_comps.get(klass.comp_id):
                    arr_comps[klass.comp_id] = 0

                if properties.get(klass.comp_id):
                    if properties[klass.comp_id].get(arr_comps[klass.comp_id]):
                        initial_props = properties[klass.comp_id][arr_comps[klass.comp_id]]

                arr_comps[klass.comp_id] += 1

            else:
                initial_props = properties.get(klass.comp_id)

            prefab_component.apply_to_entity(entity, initial_props)

        return entity
