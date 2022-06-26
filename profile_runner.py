from __future__ import annotations

import pecs
import random

DEFAULT_MAX_HEALTH = 100


class Position(pecs.Component):
    """Representation of an Entity's position."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y


class Velocity(pecs.Component):
    """Representation of an Entity's velocity."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    def on_test_event(self, evt: pecs.EntityEvent) -> pecs.EntityEvent:
        return evt


class Health(pecs.Component):
    """Representation of an Entity's health."""

    def __init__(self, maximum: int = DEFAULT_MAX_HEALTH) -> None:
        self.maximum = maximum
        self.current = maximum

    def is_alive(self) -> bool:
        return self.current > 0

    def reduce(self, amount: int) -> None:
        self.current = max(self.current - amount, 0)

    def on_damage_taken(self, evt: pecs.EntityEvent) -> None:
        self.reduce(evt.data.damage)
        evt.handle()


class Attacker(pecs.Component):

    def __init__(self, strength: int) -> None:
        self.strength = strength

    def on_attack(self, evt: pecs.EntityEvent):
        target = evt.data.target
        target.fire_event('damage_taken', {
            'damage': self.strength * evt.data.multiplier
        })
        evt.handle()


class IsFrozen(pecs.Component):
    """Flag Component denoting a frozen Entity."""


def run():
    engine = pecs.Engine()
    world = engine.create_world()
    engine.register_component(Position)
    engine.register_component(Velocity)
    engine.register_component(Health)
    engine.register_component(IsFrozen)
    engine.register_component(Attacker)

    # ~1 second for 100,000 entities
    for _ in range(1000):
        entity = world.create_entity()
        entity.add(Position, {'x': random.randint(-50, 50), 'y': random.randint(-50, 50)})
        entity.add(Velocity, {'x': 0, 'y': 0})
        entity.add(Health, {'maximum': random.randint(50, 300)})
        entity.add(Attacker, {'strength': random.randint(10, 50)})

    for _ in range(1000):
        entity = world.create_entity()
        entity.add(Position, {'x': random.randint(-50, 50), 'y': random.randint(-50, 50)})
        entity.add(Velocity, {'x': 0, 'y': 0})
        entity.add(Health, {'maximum': random.randint(50, 300)})

    pacifists = world.create_query(all_of = [Position], none_of = [Attacker])
    attackers = world.create_query(all_of = [Position, Attacker])

    for pacifist in pacifists.result:
        position: Position = pacifist.get(Position)
        velocity: Velocity = pacifist.get(Velocity)
        position.x += velocity.x
        position.y += velocity.y

    for attacker in attackers.result:
        for pacifist in pacifists.result:
            attacker.fire_event('attack', {
                'target': pacifist,
            })
