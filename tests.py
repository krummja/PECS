from __future__ import annotations

import unittest
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


class TestBase(unittest.TestCase):

    ecs: pecs.Engine
    world: pecs.World

    def setUp(self):
        self.test_initializer()

    def test_initializer(self) -> unittest.TestCase:
        self.ecs = pecs.Engine()
        self.ecs.register_component(Position)
        self.ecs.register_component(Velocity)
        self.ecs.register_component(Health)
        self.ecs.register_component(IsFrozen)
        self.ecs.register_component(Attacker)
        self.world = self.ecs.create_world()
        return self.initialize_entities(50)

    def initialize_entities(self, count: int = 10) -> unittest.TestCase:
        for _ in range(count):
            entity = self.world.create_entity()
            entity.add(Position, {'x': random.randint(-50, 50), 'y': random.randint(-50, 50)})
            entity.add(Velocity, {'x': 0, 'y': 0})
            entity.add(Health, {'maximum': random.randint(50, 300)})
        for _ in range(count // 2):
            entity = self.world.create_entity()
            entity.add(Position, {'x': random.randint(-50, 50), 'y': random.randint(-50, 50)})
            entity.add(Velocity, {'x': 0, 'y': 0})
            entity.add(Health, {'maximum': random.randint(50, 300)})
            entity.add(IsFrozen)
        return self


class EntityTests(unittest.TestCase):

    def setUp(self):
        self.ecs = pecs.Engine()
        self.ecs.register_component(Position)
        self.ecs.register_component(Velocity)
        self.ecs.register_component(Health)
        self.ecs.register_component(IsFrozen)
        self.ecs.register_component(Attacker)

        self.world = self.ecs.create_world()

        self.entity = self.world.create_entity()
        self.entity.add(Position)
        self.entity.add(Health)

        self.entity2 = self.world.create_entity()
        self.entity2.add(Health, { 'maximum': 50 })

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

    def test_entity_property_indexing(self):
        zombie = self.world.create_entity("Zombie A")
        zombie.add(Position, { 'x': 100, 'y': 100 })
        zombie.add(Velocity, { 'x': 10, 'y': 10 })
        zombie.add(Health, { 'maximum': 20 })
        zombie.add(IsFrozen)
        self.assertTrue(zombie[Position].x == 100)
        self.assertTrue(zombie[Health].current == 20)
        self.assertTrue(zombie[Velocity].x == 10)
        self.assertTrue(zombie[IsFrozen])

    def test_entity_events(self):
        player = self.world.create_entity("Player")
        player.add(Velocity, { 'x': 10, 'y': 10 })
        player.add(Health, { 'maximum': 200 })
        zombie = self.world.create_entity("Zombie")
        result = player.fire_event('test_event', {
            'target': zombie
        })

        self.assertTrue(result.data.target == zombie)
        self.assertFalse(result.data.target is None)

    def test_target_fire_event(self):
        survivor = self.world.create_entity()
        survivor.add(Health, { 'maximum': 100 })
        survivor.add(Attacker, {'strength': 5 })

        zombie = self.world.create_entity()
        zombie.add(Health, { 'maximum': 25 })
        zombie.add(Attacker, { 'strength': 25 })

        zombie.fire_event('attack', {
            'target': survivor,
            'multiplier': 1.5
        })

        survivor_health: Health = survivor[Health]
        self.assertTrue(survivor_health.current == 62.5)

    def test_entity_has_component(self):
        self.assertTrue(self.entity.has(Position))


class QueryTests(TestBase):

    def test_entityCount(self):
        self.assertTrue(len(self.world.entities) == 75)

    def test_queryCreation(self):
        query1 = self.world.create_query(
            all_of=[Position, Velocity]
        )

        query2 = self.world.create_query(
            all_of=[Position, Velocity],
            none_of=[IsFrozen]
        )

        self.assertTrue(len(query1.result) == 75)
        self.assertTrue(len(query2.result) == 50)


class ComponentTests(TestBase):

    def test_component_add_remove(self):
        entity = self.world.create_entity()
        entity.add(Position, { 'x': 0, 'y': 0 })
        self.assertTrue(entity.has(Position))

        entity.remove(Position)
        self.assertFalse(entity.has(Position))

    def test_entity_destroy(self):
        entity = self.world.create_entity('TEST')
        entity.add(IsFrozen)
        self.assertTrue(entity.has(IsFrozen))
        entity.destroy()
        self.assertTrue(self.world.get_entity('TEST').is_destroyed)
        self.assertFalse(entity.has(IsFrozen))


class PrefabTests(TestBase):

    def test_prefab_creation(self):
        self.ecs.prefabs.register({
            "name": "Test",
            "components": [
                {
                    "type": "Position",
                    "properties": {
                        "x": 10,
                        "y": 10,
                    }
                },
                {
                    "type": "Health",
                }
            ]
        })

        entity = self.ecs.prefabs.create(self.world, "Test", {
            "position": {
                "x": 50,
                "y": 50,
            },
            "health": {
                "maximum": 200
            }
        })

        self.assertTrue(entity[Position].x == 50)
        self.assertTrue(entity[Health].maximum == 200)


if __name__ == '__main__':
    unittest.main()
