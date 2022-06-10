from __future__ import annotations

import unittest
import pecs


class Position(pecs.Component):
    """Representation of an Entity's position."""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Velocity(pecs.Component):
    """Representation of an Entity's velocity."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y


class Health(pecs.Component):
    """Representation of an Entity's health."""

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum
        self.current = maximum

    def is_alive(self) -> bool:
        return self.current > 0

    def reduce(self, amount: int) -> None:
        self.current = max(self.current - amount, 0)

    def on_damage_taken(self, evt: pecs.EntityEvent) -> None:
        self.reduce(evt.data.damage)
        evt.handle()


class IsFrozen(pecs.Component):
    """Flag Component denoting a frozen Entity."""


class EntityTest(unittest.TestCase):

    def setUp(self):
        self.entities = [
            pecs.Entity("zombie A"),
            pecs.Entity("zombie B"),
        ]

        self.entity = pecs.Entity('TEST')
        self.entity[Position] = Position(10, 10)
        self.entity.add(Health(100))

        self.entity2 = pecs.Entity('TEST 2')
        self.entity2[Health] = Health(50)

    def test_entity_initialization(self):
        self.assertTrue(self.entity)
        self.assertTrue(self.entity[Position] is not None)
        self.assertTrue(self.entity.get(Position) is not None)

    def test_components_instantiated(self):
        health: Health = self.entity.get(Health)
        health.reduce(4)
        self.assertTrue(self.entity.get(Health).current == 96)

        health: Health = self.entity2.get(Health)
        health.reduce(20)
        self.assertTrue(self.entity2.get(Health).current == 30)
        self.assertTrue(self.entity2.get(Health).current != self.entity.get(Health).current)

    def test_multiple_components(self):
        pass

    def test_entity_property_indexing(self):
        zombie = pecs.Entity("Zombie A")
        zombie[Position] = Position(100, 100)
        zombie[Velocity] = { 'x': 10, 'y': 10 }
        zombie.add(Health, { 'maximum': 20 })
        zombie.add(IsFrozen())
        self.assertTrue(zombie[Position].x == 100)
        self.assertTrue(zombie[Health].current == 20)
        self.assertTrue(zombie[Velocity].x == 10)
        self.assertTrue(zombie['health'].current == 20)
        self.assertTrue(zombie[IsFrozen])


if __name__ == '__main__':
    unittest.main()
