from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    pass

from pecs.component import ComponentMeta
from collections import OrderedDict
from pecs.component import Component


class Entity:

    def __init__(self, uid: str) -> None:
        self._cbits = 0
        self._components = OrderedDict()
        self._qeligible = True
        self._uid = uid
        self._index = 0

    def __getitem__(self, component_class_or_name: ComponentMeta | str) -> Any:
        if isinstance(component_class_or_name, str):
            for key, value in self._components.items():
                if key.comp_id == component_class_or_name.upper():
                    return value
        return self._components.get(component_class_or_name)

    def __setitem__(
            self,
            component_class: ComponentMeta,
            component_or_properties: Component | Dict[str, Any]
        ) -> None:
        if isinstance(component_or_properties, Component):
            self._components[component_class] = component_or_properties
        elif isinstance(component_or_properties, dict):
            self._components[component_class] = component_class(**component_or_properties)

    def __str__(self) -> str:
        return self._uid

    def __hash__(self) -> int:
        return hash(self._uid)

    def __len__(self) -> int:
        return len(self._components)

    def __iter__(self) -> Entity:
        return self

    def __next__(self):
        if self._index > len(self) - 1:
            raise StopIteration
        component = list(self._components.values())[self._index]
        self._index += 1
        return component

    def __contains__(self, component_class: ComponentMeta) -> bool:
        return self._components.__contains__(component_class)

    def add(
            self,
            component: Component | ComponentMeta,
            component_properties: Optional[Dict[str, Any]] = None
        ) -> None:
        """Add a new Component instance to this Entity."""
        if isinstance(component, ComponentMeta) and component_properties is not None:
            instance = component(**component_properties)
            self._components[component] = instance
        elif isinstance(component, Component):
            self._components[component.__class__] = component
        else:
            raise Exception(f"Invalid Component initializer! Aborting.")

    def get(self, component_class_or_name: ComponentMeta | str) -> Any:
        """Get a Component currently attached to this Entity."""
        if isinstance(component_class_or_name, str):
            for key, value in self._components.items():
                if key.comp_id == component_class_or_name.upper():
                    return value
        return self._components.get(component_class_or_name)
