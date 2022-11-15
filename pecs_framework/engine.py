from __future__ import annotations
from beartype import beartype
from beartype.typing import *
from collections import OrderedDict

if TYPE_CHECKING:
    from pecs_framework.component import IdStr

from pecs_framework.utils import *
from pecs_framework.component import Component
from pecs_framework.domain import Domain, Entity
from pecs_framework.component import ComponentMeta


CInst = TypeVar("CInst", bound=Component)


class ComponentRegistry:
    
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._cbits = 1
        self._map: OrderedDict[IdStr, ComponentMeta] = OrderedDict()
        
    @beartype
    def register(self, component: ComponentMeta) -> None:
        key = component.__name__.upper()
        component.cbits = self._cbits
        self._map[key] = component
        self._cbits += 1

    def get(self, key: str) -> type[CInst]:
        _key: IdStr = key.upper()
        return cast(type[CInst], self._map[_key])


class Accessor(Generic[CInst]):
    
    def __init__(self, ecs: Engine, component: type[CInst]) -> None:
        self._registry = ecs.components
        self._component = component

    def unwrap(self) -> type[CInst]:
        return self._registry.get(self._component.__name__.upper())
        

class Engine:
    
    def __init__(self) -> None:
        self.domain = Domain(self)
        self.components = ComponentRegistry(self)
        
    def get_component(self, component_name: str) -> type[CInst]:
        """
        Get a Component type from the ECS Component Registry by its component
        identifier (the name of the Component type).

        Parameters
        ----------
        component_name
            Case-insensitive string identifier of a registered Component type

        Returns
        -------
            The Component type, if it is registered

        Example
        -------
        ```py
        e1 = ecs.domain.create_entity()
        position = ecs.get_component('position')(10, 10)
        ecs.attach_component(e1, position)
        ```
        """
        component_ = self.components.get(component_name)
        return Accessor(self, component_).unwrap()
    
    def attach_component_type(
            self,
            entity: Entity | str,
            component: ComponentMeta,
            properties: dict[str, Any],
        ) -> None:
        """
        Attach a Component type to an Entity. Requires instantiation by
        additionally passing a dict that maps to the Component kwargs.

        Parameters
        ----------
        entity
            An Entity instance or a string alias to an Enttity
        component
            An uninstantiated Component type
        properties
            A dict representing the kwargs of the Component's `__init__`
            
        Example
        -------
        ```py
        e1 = ecs.domain.create_entity()
        ecs.attach_and_initialize_component(e1, Position, {'x': 10, 'y': 0})
        ```
        """
        if isinstance(entity, str):
            entity_: Entity = self.domain.get_entity_by_alias(entity)
        else:
            entity_: Entity = self.domain.entities[entity.eid]
        
        key = component.comp_id
        properties_ = properties if properties else {}
        cbit = component.cbits
        component_ = component(**properties_)
        
        entity_.cbits = add_bit(entity_.cbits, cbit)
        entity_.components[key] = component_
    
    def attach_component(self, entity: Entity | str, component: CInst) -> None:
        """
        Attach a Component instance to an Entity.

        Parameters
        ----------
        entity
            An Entity instance or a string alias to an Entity
        component
            A Component instance

        Example
        -------
        ```py
        e1 = ecs.domain.create_entity()
        ecs.attach_component(e1, Position(x: 10, y: 0))
        ```
        """
        if isinstance(entity, str):
            entity_: Entity = self.domain.get_entity_by_alias(entity)
        else:
            entity_: Entity = self.domain.entities[entity.eid]

        key = component.classtype.comp_id
        cbit = component.classtype.cbits
        component_ = component
            
        entity_.cbits = add_bit(entity_.cbits, cbit)
        entity_.components[key] = component_
