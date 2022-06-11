from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.component import Component, ComponentMeta

from pecs.world import World
from pecs.component_registry import ComponentRegistry
from pecs.prefab_registry import PrefabRegistry


class Engine:

    def __init__(self) -> None:
        self.components = ComponentRegistry(self)
        self.prefabs = PrefabRegistry(self)

    def create_world(self):
        return World(self)

    def register_component(self, component: ComponentMeta) -> None:
        self.components.register(component)
