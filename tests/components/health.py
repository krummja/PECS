from __future__ import annotations

from dataclasses import dataclass, field
from pecs_framework.component import Component
from pecs_framework.events import EntityEvent


@dataclass
class Health(Component):
    """Representation of an Entity's health."""
    maximum: int = 100
    current: int = field(init=False)

    def __post_init__(self) -> None:
        self.current = self.maximum

    def on_damage_taken(self, evt: EntityEvent) -> EntityEvent:
        damage = evt.data.amount
        self.current -= damage
        evt.handle()
        return evt
