from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs_framework.engine import Engine

from collections import OrderedDict
from pecs_framework.helpers import *
from pecs_framework.component import Component, ComponentMeta
from pecs_framework.entity_event import EntityEvent, EventData


def remove_component(entity: Entity, component: ComponentMeta) -> None:
    del entity.components[component]
    entity._cbits = subtract_bit(entity.cbits, component.cbit)
    entity.candidacy()


class Entity:

    def __init__(self, engine: Engine, uid: str) -> None:
        self.is_destroyed = False

        self._engine = engine
        self._cbits = 0
        self._components = OrderedDict()
        self._qeligible = True
        self._uid = uid
        self._index = 0

    def __getitem__(self, component_class_or_name: ComponentMeta) -> Any:
        return self._components.get(component_class_or_name)

    def __str__(self) -> str:
        return self._uid

    def __hash__(self) -> int:
        return hash(self._uid)

    def __len__(self) -> int:
        return len(self._components)

    def __iter__(self) -> OrderedDict[ComponentMeta, Component]:
        return self._components

    def __next__(self):
        if self._index > len(self) - 1:
            raise StopIteration
        component = list(self._components.values())[self._index]
        self._index += 1
        return component

    def __contains__(self, component_class: ComponentMeta) -> bool:
        return self._components.__contains__(component_class)

    @property
    def cbits(self) -> int:
        return self._cbits

    @property
    def components(self) -> OrderedDict[ComponentMeta, Component]:
        return self._components

    def candidacy(self) -> None:
        if self._qeligible:
            self._engine.world.candidate(self)

    def add(
            self,
            component: ComponentMeta,
            component_properties: Optional[Dict[str, Any]] = None
        ) -> None:
        """Add a new Component instance to this Entity."""
        if isinstance(component, ComponentMeta):
            properties = component_properties or {}
            component_class = self._engine.components[component.comp_id]

            instance: Component = component_class(**properties)
            instance.attach(self)

            self._components[component] = instance
            self._cbits = add_bit(self._cbits, instance.cbit)
            self.candidacy()

        else:
            raise Exception("Invalid Component initializer! Aborting.")

    def get(self, component_class_or_name: ComponentMeta) -> Any:
        """Get a Component currently attached to this Entity."""
        return self._components.get(component_class_or_name)

    def has(self, component: ComponentMeta) -> bool:
        instance: Component | None = self.get(component)
        if instance is None:
            return False
        return has_bit(self._cbits, instance.cbit)

    def owns(self, component: ComponentMeta) -> bool:
        instance: Component = self.get(component)
        return instance.entity == self

    def remove(self, component: ComponentMeta) -> None:
        remove_component(self, component)

    def destroy(self) -> None:
        to_destroy = []
        for name, component in self._components.items():
            to_destroy.append(component)
        for component in to_destroy:
            self.remove(component)
            component.destroy()
        self._engine.world.destroy_entity(self._uid)
        self._components.clear()
        self.is_destroyed = True

    def serialize(self) -> str:
        pass

    def fire_event(
            self,
            event: str,
            data: Optional[Dict[str, Any] | EventData] = None
        ) -> EntityEvent:
        if isinstance(data, EventData):
            data = data.record
        else:
            data = data or {}

        evt = EntityEvent(event, data)
        for component in self.components.values():
            component.handle_event(evt)
            if evt.prevented:
               return evt
        return evt
