from __future__ import annotations
from beartype import beartype
from beartype.typing import TYPE_CHECKING
from beartype.typing import cast
from beartype.typing import Any
from types import ModuleType
from collections import OrderedDict

if TYPE_CHECKING:
    from pecs_framework._types import CompId
    from pecs_framework.loader import Loader

from pecs_framework.component import ComponentMeta, Component
from pecs_framework.domain import Domain, EntityRegistry
from pecs_framework.entity import add_component
from pecs_framework.entity import add_component_type
from pecs_framework.entity import Entity
from pecs_framework.entity import has_component
from pecs_framework.entity import remove_component
from pecs_framework.prefab import PrefabBuilder


class ComponentRegistry:

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._cbits = 0
        self._map: OrderedDict[CompId, ComponentMeta] = OrderedDict()

    def load(self) -> None:
        if self._engine._loader:
            loader = self._engine._loader
            loader.load()
            for component in loader.components:
                self.register(component)

    @beartype
    def register(self, component: ComponentMeta) -> None:
        key = component.__name__.upper()
        if key in self._map.keys():
            return
        component.cbit = self._cbits
        self._map[key] = component
        self._cbits += 1

    @beartype
    def get_type(self, key: ComponentMeta | str) -> type[Component]:
        if isinstance(key, str):
            _key: CompId = key.upper()
        else:
            _key = key.comp_id
        return cast(type[Component], self._map[_key])

    @beartype
    def attach(
        self,
        entity: Entity,
        component: ComponentMeta | str | Component,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """
        Attach a Component to an Entity.

        A Component in this context can be a ComponentType (an uninstantiated
        Component class), a Component instance, or a string component name.

        Examples
        --------
        ```py
        ecs.components.attach(some_entity, Position(10, 10))
        ecs.components.attach(some_entity, "health", {"maximum": 150})
        ecs.components.attach(some_entity, IsFrozen)
        ```

        Parameters
        ----------
        entity
            The Entity to which this Component will be attached
        component
            A ComponentType, Component instance, or a Component name
        properties, optional
            A dict of arguments to pass to a Component class, by default None
        """
        if isinstance(component, str):
            component = self._map[component.upper()]

        if isinstance(component, ComponentMeta):
            properties_ = properties if properties else {}
            add_component_type(entity, component, properties_)
        else:
            add_component(entity, component)

    @beartype
    def remove(
        self,
        entity: Entity,
        component: ComponentMeta | str | Component
    ) -> None:
        if not isinstance(component, ComponentMeta):
            if isinstance(component, str):
                component = self._map[component.upper()]
            else:
                component = component.__class__

        remove_component(entity, component)

    @beartype
    def has(self, entity: Entity, component_type: ComponentMeta) -> bool:
        if not entity:
            return False
        return has_component(entity, component_type)


class Engine:

    def __init__(self, loader: Loader | None = None) -> None:
        """
        The core ECS engine, providing access to the Domain and
        ComponentRegistry objects.
        """
        self._domain: Domain
        self._components: ComponentRegistry
        self._prefabs: PrefabBuilder
        self._domains = {}
        self._registries = {}
        self._loader = loader

    @property
    def domain(self) -> Domain:
        return self._domain

    @property
    def entities(self) -> EntityRegistry:
        return self._domain.entities

    @property
    def components(self) -> ComponentRegistry:
        return self._components

    @property
    def prefabs(self) -> PrefabBuilder:
        return self._prefabs

    def create_domain(self, domain_name: str) -> Domain:
        """
        Create a new Domain.

        Parameters
        ----------
        domain_name
            The name to use as the Domain's primary identifier

        Returns
        -------
            The newly created Domain instance
        """
        self._domains[domain_name] = Domain(self)
        self._registries[domain_name] = ComponentRegistry(self)
        self._domain = self._domains[domain_name]
        self._components = self._registries[domain_name]
        self._prefabs = PrefabBuilder(self)
        return self.domain

    def change_domain(self, domain_name: str) -> Domain:
        domain = self._domains[domain_name]
        self._domain = self._domains[domain_name]
        self._components = self._registries[domain_name]
        return domain
