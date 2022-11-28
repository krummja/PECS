from __future__ import annotations

from dataclasses import dataclass, field
from pecs_framework.component import Component
from pecs_framework.events import EntityEvent
from pecs_framework.entity import Entity


@dataclass
class Attacker(Component):
    strength: int

    def on_attack(self, evt: EntityEvent) -> EntityEvent:
        target: Entity = evt.data.target
        target.fire_event('damage_taken', {
            'amount': self.strength * evt.data.multiplier,
        })
        evt.handle()
        return evt
