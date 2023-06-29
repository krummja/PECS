from __future__ import annotations
from beartype.typing import *
from beartype import beartype
from collections import OrderedDict

if TYPE_CHECKING:
    from pecs_framework._types import CompId

from pecs_framework.events import EventData, EntityEvent
from pecs_framework.component import Component, CT
from .utils import *


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
