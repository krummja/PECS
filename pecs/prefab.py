from __future__ import annotations
from typing import *

from pecs.entity import Entity
from pecs.prefab_component import PrefabComponent


class Prefab:

    def __init__(self, name: str, inherit: list[Prefab], components: list[PrefabComponent]) -> None:
        self.name = name
        self.inherit = inherit or []
        self.components = components or []

    def add_component(self, component: PrefabComponent) -> None:
        pass

    def apply_to_entity(
            self,
            entity: Entity,
            prefab_props: Optional[Dict[str, Any]] = None
        ) -> Entity:
        pass
