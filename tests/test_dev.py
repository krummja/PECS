from __future__ import annotations
from beartype.typing import TYPE_CHECKING
from typing import TypeAlias

if TYPE_CHECKING:
    from pecs_framework.engine import Engine
    from pecs_framework.prefab import EntityTemplate, ComponentTemplate

import pytest
from pecs_framework import Engine
from pecs_framework import entity as entities
from pecs_framework.base_system import BaseSystem, Loop

from .components import *
from .components import loader

import json
from rich import inspect


class MovementSystem(BaseSystem):

    def initialize(self) -> None:
        self.query(
            'movable', 
            all_of = [ Position, Velocity ],
            none_of = [ IsFrozen ],
        )
    
    def update(self) -> None:
        movables = self._queries['movable'].result
        for entity in movables:
            entity[Position].x += entity[Velocity].x
            entity[Position].y += entity[Velocity].y


class MockLoop(Loop):

    def initialize(self) -> None:
        self.movement_system = MovementSystem(self)

    def teardown(self) -> None:
        pass

    def pre_update(self) -> None:
        pass

    def update(self) -> None:
        for _ in range(20):
            self.movement_system.update()

    def post_update(self) -> None:
        pass


#! TESTS ======================================================================
#! ----------------------------------------------------------------------------

@pytest.fixture(scope="function")
def ecs() -> Engine:
    ecs = Engine(loader=loader)
    domain = ecs.create_domain('World')
    ecs.components.load("tests.components")

    domain.entities.create('e1')
    domain.entities.create('e2')
    domain.entities.create('e3')
    domain.entities.create('e4')
    domain.entities.create('e5')

    for i, entity in enumerate(domain.entities.values()):
        # Note we're using Component name with an initialization dict here.
        ecs.components.attach(entity, "position", {'x': 10, 'y': 10})

        # Passing a ComponentType with an initialization dict.
        ecs.components.attach(entity, Velocity, {'x': 1, 'y': 1})

        # In these cases we're passing Component instances. Totally fine!
        ecs.components.attach(entity, Renderable('@', (255, 0, 255), (0, 0, 0)))
        ecs.components.attach(entity, Health(100))

        # And finally we're passing a ComponentType to be instantiated on the
        # entity without arguments.
        if i > 0:
            ecs.components.attach(entity, IsFrozen)

        ecs.components.attach(entity, Attacker(10))
        
    return ecs


#* PASSING
def test_entity_creation(ecs: Engine, caplog):
    """
    Test that the Entity instances we created exist and are accessible via the
    aliases we defined.
    """
    domain = ecs.domain

    e1 = domain.entities.get_by_alias('e1')
    e2 = domain.entities.get_by_alias('e2')
    e3 = domain.entities.get_by_alias('e2')
    e4 = domain.entities.get_by_alias('e2')
    e5 = domain.entities.get_by_alias('e2')
    assert all([e1, e2, e3, e4, e5])


#* PASSING
def test_component_registration(ecs: Engine):
    """
    Test that specific Component types exist in the ECS Engine and that their 
    cbit values are what we expect.
    """
    attacker = ecs.components.get_type("Attacker")
    position = ecs.components.get_type('Position')
    velocity = ecs.components.get_type('Velocity')
    renderable = ecs.components.get_type('Renderable')

    # Getting by string is not case-sensitive.
    is_frozen = ecs.components.get_type('isfrozen')

    # Getting can also be done by Component class.
    health = ecs.components.get_type(Health)

    assert attacker.cbit == 0
    assert health.cbit == 1
    assert is_frozen.cbit == 2
    assert position.cbit == 3
    assert renderable.cbit == 4
    assert velocity.cbit == 5


#* PASSING
def test_component_attachment(ecs: Engine):
    """
    Test that our Component attachments were successful by checking that the
    Entities' cbit states correspond to what is expected for the Entity Type.
    """
    domain = ecs.domain
    e1 = domain.entities.get_by_alias('e1')
    e2 = domain.entities.get_by_alias('e2')
    e3 = domain.entities.get_by_alias('e3')
    e4 = domain.entities.get_by_alias('e4')
    e5 = domain.entities.get_by_alias('e5')

    assert ecs.components.has(e1, Velocity)
    assert ecs.components.has(e2, IsFrozen)
    assert ecs.components.has(e3, Health)
    assert ecs.components.has(e4, Position)
    assert ecs.components.has(e5, Renderable)

    e1_position: Position = entities.get_component(e1, Position)
    assert entities.owns_component(e1, e1_position)


#* PASSING
def test_component_instantiation(ecs: Engine):
    """
    Test that a Component that is attached to an Entity was instantiated with
    the correct values.
    """
    domain = ecs.domain
    e1 = domain.entities.get_by_alias('e1')
    e1_position: Position = entities.get_component(e1, Position)
    assert e1_position is not None
    assert e1_position.x == 10
    assert e1_position.y == 10
    
    
#* PASSING
def test_component_removal(ecs: Engine):
    """
    Test that a Component that is attached to an Entity was removed when a
    Component removal is requested.
    """
    domain = ecs.domain
    e3 = domain.entities.get_by_alias('e3')
    assert ecs.components.has(e3, Position)
    ecs.components.remove(e3, Position)
    assert not ecs.components.has(e3, Position)    


#* PASSING
def test_entity_destruction(ecs: Engine):
    """
    Test that an Entity that currently exists in the Domain is destroyed when
    an Entity destruction is requested.
    """
    domain = ecs.domain
    entity1 = domain.entities.create('delete_1')
    entity2 = domain.entities.create('delete_2')
    entity3 = domain.entities.create('delete_3')
    
    assert entity1.eid in domain.entities.keys()
    assert entity2.eid in domain.entities.keys()
    assert entity3.eid in domain.entities.keys()

    domain.destroy_entity('delete_1')
    assert entity1.eid not in domain.entities.keys()

    domain.destroy_entity(entity2)
    assert entity2.eid not in domain.entities.keys()

    domain.destroy_entity(entity3.eid)
    assert entity3.eid not in domain.entities.keys()


#* PASSING
def test_component_destruction_with_entity(ecs: Engine):
    """
    Test that when an Entity is destroyed, all of its attached Components are
    destroyed as well.
    """
    domain = ecs.domain
    entity = domain.entities.create('entity')
    ecs.components.attach(entity, Position(10, 10))
    ecs.components.attach(entity, IsFrozen)

    assert entities.has_component(entity, Position)
    assert entities.has_component(entity, IsFrozen)

    position = entities.get_component(entity, Position)
    frozen = entities.get_component(entity, IsFrozen)

    assert position is not None
    assert frozen is not None
    domain.destroy_entity(entity)

    assert position.entity_id == ''
    assert frozen.entity_id == ''


# TODO
def test_on_component_added(ecs: Engine):
    pass


# TODO
def test_on_component_removed(ecs: Engine):
    pass


#* PASSING
def test_multidomain(ecs: Engine):
    """
    Test the Domain switching feature.
    """
    domain = ecs.domain
    assert domain == ecs._domains['World']

    new_domain = ecs.create_domain('New Domain')
    assert ecs.domain == new_domain

    domain = ecs.change_domain('World')
    assert ecs.domain == ecs._domains['World']


#* PASSING
def test_component_query(ecs: Engine):
    """
    Test Component querying. This is crucial to system creation and the heart
    of the ECS core functionality.
    """
    domain = ecs.domain

    movable = domain.create_query(
        all_of = [ 
            Position, 
            Velocity,
        ],
        none_of = [
            IsFrozen,
        ],
    )
    assert len(movable.result) == 1
    

#* PASSING
def test_system_behavior(ecs: Engine):
    """
    Test that a system using a Query can modify the state of Component 
    instances attached to Entity instances as expected.

    In this case, a single loop will perform 20 ticks. Since the current
    Velocity component is set to {'x': 1, 'y': 1}, and the starting Position
    is {'x': 10, 'y': 10}, we expect to see a value of {'x': 30, 'y': 30} after
    the system has performed its update loop.
    """
    domain = ecs.domain    
    e1 = domain.entities.get_by_alias('e1')

    assert e1[Position].x == 10
    assert e1[Position].y == 10
    
    test_loop = MockLoop(ecs, domain)
    test_loop.update()

    assert e1[Position].x == 30
    assert e1[Position].y == 30


def test_entity_events(ecs: Engine):
    """
    Test EntityEvent and EventData classes.

    This test is successful in case that an event is fired against an entity's
    Attacker component, which results in the secondary firing of an event
    against a target entity's Health component.

    The attacking entity should deal 15 damage to the attacked entity.
    """
    domain = ecs.domain
    e1 = domain.entities.get_by_alias('e1')

    assert e1[Attacker].strength == 10

    e1.fire_event('attack', {
        'target': domain.entities.get_by_alias('e2'),
        'multiplier': 1.5,
    })

    e2 = domain.entities.get_by_alias('e2')

    assert e2[Health].maximum == 100
    assert e2[Health].current == e2[Health].maximum - 15


#* PASSING
def test_component_loader(ecs: Engine):
    assert len(ecs.components._map) == 6


# TODO
def test_serialization(ecs: Engine):
    pass


#* PASSING
def test_deserialization(ecs: Engine):
    """Test prefab definition unpacking into the correct objects."""
    prefabs = ecs.prefabs

    definition = json.dumps({
        "name": "GameObject",
        "inherit": [],
        "components": [
            {
                "type": "Position",
            },
            {
                "type": "Renderable",
                "properties": {
                    "char": "?"
                }
            },
            {
                "type": "Noun",
                "properties": {
                    "text": "<unset>"
                }
            }
        ]  
    })    

    template: EntityTemplate = prefabs.deserialize(definition)

    assert template['name'] == "GameObject"
    assert len(template['inherit']) == 0
    assert len(template['components']) == 3

    components: list[ComponentTemplate] = template['components']

    assert components[0]['component_type'] == "Position"
    assert components[1]['properties']['char'] == '?'


# TODO
def test_component_prefab(ecs: Engine):
    pass


# TODO
def test_entity_prefab(ecs: Engine):
    pass
