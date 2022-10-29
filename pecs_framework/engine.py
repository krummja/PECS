from __future__ import annotations

from pecs_framework.component import ComponentMeta
from pecs_framework.world import World
from pecs_framework.component_registry import ComponentRegistry
from pecs_framework.prefab_registry import PrefabRegistry


class Engine:

    world: World

    def __init__(self) -> None:
        self.components = ComponentRegistry(self)
        self.prefabs = PrefabRegistry(self)

    def create_world(self):
        """Creates a new World instance to bind to this Engine.

        :return:
            The created World instance.
        """
        self.world = World(self)
        return self.world

    def register_component(self, component_class: ComponentMeta) -> None:
        """Add a Component class to the ComponentRegistry for later
        instantiation.

        :param component_class:
            The Component class to register. Note that this must be the
            *class* and not an instance of a Component.
        """
        self.components.register(component_class)
