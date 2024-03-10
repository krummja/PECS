from __future__ import annotations
from beartype import beartype
from beartype.typing import TYPE_CHECKING
from beartype.typing import Any
from beartype.typing import cast
from collections import OrderedDict

if TYPE_CHECKING:
    from pecs_framework._types import CompId
    from pecs_framework.domain import Domain
    from .entity import Entity

import json
from pecs_framework.events import EventData, EntityEvent
from pecs_framework.utils import has_bit
from pecs_framework.utils import subtract_bit
from pecs_framework.utils import add_bit
from pecs_framework.component import Component
from pecs_framework.component import ComponentMeta
from pecs_framework.component import CT


class Entity:

    @beartype
    def __init__(self, domain, entity_id: str = '') -> None:
        self.domain = domain
        self.eid = entity_id
        self.cbits: int = 0
        self.components: OrderedDict[CompId, Component] = OrderedDict()
        self.qeligible: bool = True

    def __getitem__(self, component: type[CT] | str) -> CT:
        if isinstance(component, str):
            _component = self.domain.engine.components.get_type(component)
        else:
            _component = component
        return cast(CT, get_component(self, _component))

    def fire_event(
        self,
        event: str,
        data: dict[str, Any] | EventData | None = None
    ) -> EntityEvent:
        """
        Fire an event to all subscribed components attached to this entity.

        The event name should be a simple, snake-cased string. Subscribed
        components must implement a handler method that takes in an
        `EntityEvent` and returns that event.

        ## Example

        ```py
        @dataclass
        class Health(Component):
            '''Representation of an Entity's health.'''
            maximum: int = 100
            current: int = field(init=False)

            def __post_init__(self) -> None:
                self.current = self.maximum

            def on_damage_taken(self, evt: EntityEvent) -> EntityEvent:
                damage = evt.data.amount
                self.current -= damage
                evt.handle()
                return evt
        ```
        """
        if data and isinstance(data, EventData):
            data = data.record
        elif data and isinstance(data, dict):
            data = EventData(**data).record
        else:
            data = {}
        evt = EntityEvent(event, data)

        for component in self.components.values():
            component.handle_event(evt)
            if evt.prevented:
                return evt
        return evt

    def on_component_added(self):
        pass

    def on_component_removed(self):
        pass

    def on_entity_destroyed(self):
        pass

    def _on_component_added(self):
        candidacy(self.domain, self)
        self.on_component_added()

    def _on_component_removed(self):
        candidacy(self.domain, self)
        self.on_component_removed()

    def _on_entity_destroyed(self):
        to_delete = []
        for component in self.components.values():
            to_delete.append(component)

        for component in to_delete:
            self.components[component.comp_id]._entity_id = ''
            del self.components[component.comp_id]

        self.on_entity_destroyed()


def add_component_type(
    entity: Entity,
    component: ComponentMeta,
    properties: dict[str, Any] | None = None,
) -> None:
    """
    Add a Component class and instantiate it on the Entity.

    If the Component class requires parameters, these can be passed as a
    properties dictionary.

    Parameters
    ----------
    entity
        The Entity to add the Component class to
    component
        The Component class to add to the Entity
    properties, optional
        Parameter dict for Component class instantiation, by default None
    """
    entity.cbits = add_bit(entity.cbits, component.cbit)
    if properties:
        entity.components[component.comp_id] = component(**properties)
    else:
        entity.components[component.comp_id] = component()
    entity.components[component.comp_id]._entity_id = entity.eid
    entity._on_component_added()


def add_component(entity: Entity, component: Component) -> None:
    """
    Add a Component instance to an Entity.

    Parameters
    ----------
    entity
        The Entity to add the Component instance to
    component
        The Component instance to add to the Entity
    """
    entity.cbits = add_bit(entity.cbits, component.__class__.cbit)
    entity.components[component.__class__.comp_id] = component
    component._entity_id = entity.eid
    entity._on_component_added()


def remove_component(entity: Entity, component_type: ComponentMeta) -> None:
    comp_id: CompId = component_type.comp_id
    instance = entity.components[comp_id]
    entity.cbits = subtract_bit(entity.cbits, component_type.cbit)
    entity._on_component_removed()
    del entity.components[comp_id]
    del instance


def owns_component(entity: Entity, component: Component) -> bool:
    return component.entity_id == entity.eid


def has_component(entity: Entity, component_type: ComponentMeta) -> bool:
    return has_bit(entity.cbits, component_type.cbit)


def get_component(entity: Entity, component_type: type[CT]) -> CT:
    try:
        if isinstance(component_type, str):
            component = entity.components[component_type.title()]
        else:
            component = entity.components[component_type.comp_id]
        return cast(CT, component)
    except Exception as exc:
        exc.add_note("Component was not found in the entity's component list.")
        raise


def candidacy(domain: Domain, entity: Entity) -> None:
    if entity.qeligible:
        domain.candidate(entity)


def serialize_component(component: Component) -> str:
    return json.dumps(component.__dict__)
