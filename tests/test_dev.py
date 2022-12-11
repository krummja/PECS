from __future__ import annotations
from beartype.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pecs_framework.engine import Engine
    from pecs_framework.prefab import EntityTemplate, ComponentTemplate

import os
import pytest

from pecs_framework import Engine
from pecs_framework.base_system import BaseSystem, Loop
from pecs_framework.entities.utils import *

from tests.components import *
from tests.components import loader

import json


TEST_DIR = os.path.dirname(__file__)
PREFABS = os.path.join(TEST_DIR, 'prefabs')


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
    
    ecs.prefabs.register(PREFABS, 'game_object')
    ecs.prefabs.register(PREFABS, 'character')
    ecs.prefabs.register(PREFABS, 'player')
    ecs.prefabs.register(PREFABS, "combatant")
    ecs.prefabs.register(PREFABS, "human_attacker")

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


@pytest.fixture(scope="function")
def prefab() -> str:
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
                    "ch": "?"
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
    return definition


#* PASSING
def test_entity_creation(ecs: Engine, caplog) -> None:
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
def test_component_registration(ecs: Engine) -> None:
    """
    Test that specific Component types exist in the ECS Engine and that their 
    cbit values are what we expect.
    """
    attacker = ecs.components.get_type("Attacker")
    position = ecs.components.get_type('Position')
    velocity = ecs.components.get_type('Velocity')
    renderable = ecs.components.get_type('Renderable')
    noun = ecs.components.get_type('Noun')

    # Getting by string is not case-sensitive.
    is_frozen = ecs.components.get_type('isfrozen')

    # Getting can also be done by Component class.
    health = ecs.components.get_type(Health)

    assert attacker.cbit == 0
    assert health.cbit == 1
    assert is_frozen.cbit == 2
    assert noun.cbit == 3
    assert position.cbit == 4
    assert renderable.cbit == 5
    assert velocity.cbit == 6


#* PASSING
def test_component_attachment(ecs: Engine) -> None:
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

    e1_position: Position = get_component(e1, Position)
    assert owns_component(e1, e1_position)


#* PASSING
def test_component_instantiation(ecs: Engine) -> None:
    """
    Test that a Component that is attached to an Entity was instantiated with
    the correct values.
    """
    domain = ecs.domain
    e1 = domain.entities.get_by_alias('e1')
    e1_position: Position = get_component(e1, Position)
    assert e1_position is not None
    assert e1_position.x == 10
    assert e1_position.y == 10
    
    
#* PASSING
def test_component_removal(ecs: Engine) -> None:
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
def test_entity_destruction(ecs: Engine) -> None:
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
def test_component_destruction_with_entity(ecs: Engine) -> None:
    """
    Test that when an Entity is destroyed, all of its attached Components are
    destroyed as well.
    """
    domain = ecs.domain
    entity = domain.entities.create('entity')
    ecs.components.attach(entity, Position(10, 10))
    ecs.components.attach(entity, IsFrozen)

    assert has_component(entity, Position)
    assert has_component(entity, IsFrozen)

    position = get_component(entity, Position)
    frozen = get_component(entity, IsFrozen)

    assert position is not None
    assert frozen is not None
    domain.destroy_entity(entity)

    assert position.entity_id == ''
    assert frozen.entity_id == ''


# TODO
def test_on_component_added(ecs: Engine) -> None:
    pass


# TODO
def test_on_component_removed(ecs: Engine) -> None:
    pass


#* PASSING
def test_multidomain(ecs: Engine) -> None:
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
def test_component_query(ecs: Engine) -> None:
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
def test_system_behavior(ecs: Engine) -> None:
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


def test_entity_events(ecs: Engine) -> None:
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
def test_component_loader(ecs: Engine) -> None:
    assert len(ecs.components._map) == 7


# TODO
def test_serialization(ecs: Engine) -> None:
    pass


#* PASSING
def test_deserialization(ecs: Engine, prefab: str) -> None:
    """Test prefab definition unpacking into the correct objects."""
    template: EntityTemplate = ecs.prefabs.deserialize(prefab)

    assert template.name == 'GameObject'
    assert len(template.inherit) == 0
    assert len(template.components) == 3


#* PASSING
def test_prefab(ecs: Engine, prefab: str) -> None:
    template: EntityTemplate = ecs.prefabs.deserialize(prefab)
    components: list[ComponentTemplate] = template.components

    assert components[0].component_type == 'Position'
    assert components[1].properties['ch'] == '?'


#* PASSING
def test_entity_from_prefab(ecs: Engine) -> None:
    test_entity = ecs.domain.entities.create_from_prefab(
        template = 'Character',
        properties = {
            'Position': {
                'x': 10,
                'y': 100,
            },
            'Renderable': {
                'ch': '@',
                'fg': (255, 0, 255),
            },
            'Health': {
                'maximum': 1000,
            }
        },
        alias = 'test1',
    )

    assert ecs.components.has(test_entity, Renderable)

    renderable: Renderable = get_component(test_entity, Renderable)
    assert renderable.ch == '@'
    assert renderable.fg == (255, 0, 255)
    assert renderable.bg == (0, 0, 0)

    position: Position = get_component(test_entity, Position)
    assert position.x == 10
    assert position.y == 100

    health: Health = get_component(test_entity, Health)
    assert health.current == 1000


def test_partial_prefab_overrides(ecs: Engine) -> None:
    test_entity = ecs.domain.entities.create_from_prefab(
        template = 'Character',
        properties = {
            'Position': {
                'x': 10,
            },
            'Health': {
                'maximum': 10,
            },
            'Noun': {
                'text': 'TEST',
            },
        },
        alias = 'test2',
    )

    assert ecs.components.has(test_entity, Renderable)

    renderable: Renderable = get_component(test_entity, Renderable)
    assert renderable.ch == '#'
    assert renderable.fg == (255, 255, 255)
    assert renderable.bg == (0, 0, 0)

    position: Position = get_component(test_entity, Position)
    assert position.x == 10
    assert position.y == 0

    health: Health = get_component(test_entity, Health)
    assert health.current == 10

    noun: Noun = get_component(test_entity, Noun)
    assert noun.text == 'TEST'


def test_default_prefab(ecs: Engine) -> None:
    test_entity = ecs.domain.entities.create_from_prefab(
        template = 'Character',
        alias = 'test3',
    )

    health: Health = get_component(test_entity, Health)
    assert health.maximum == 100
    assert health.current == 100

    renderable: Renderable = get_component(test_entity, Renderable)
    assert renderable.ch == '#'
    assert renderable.fg == (255, 255, 255)
    assert renderable.bg == (0, 0, 0)

    position: Position = get_component(test_entity, Position)
    assert position.x == 0
    assert position.y == 0

    noun: Noun = get_component(test_entity, Noun)
    assert noun.text == '<unset>'


def test_deep_inheritance(ecs: Engine) -> None:
    player = ecs.domain.entities.create_from_prefab(
        template = 'Player',
        alias = 'PLAYER',
    )

    health: Health = get_component(player, Health)
    assert health.maximum == 100
    assert health.current == 100

    renderable: Renderable = get_component(player, Renderable)
    assert renderable.ch == '@'
    assert renderable.fg == (255, 0, 255)
    assert renderable.bg == (0, 0, 0)

    position: Position = get_component(player, Position)
    assert position.x == 0
    assert position.y == 0

    noun: Noun = get_component(player, Noun)
    assert noun.text == 'PLAYER'


def test_multi_inheritance(ecs: Engine) -> None:
    combatant = ecs.domain.entities.create_from_prefab(
        template = 'Human Attacker',
        alias = 'Attacker',
    )

    health: Health = get_component(combatant, Health)
    assert health.maximum == 100
    assert health.current == 100

    renderable: Renderable = get_component(combatant, Renderable)
    assert renderable.ch == '#'
    assert renderable.fg == (255, 255, 255)
    assert renderable.bg == (0, 0, 0)

    position: Position = get_component(combatant, Position)
    assert position.x == 0
    assert position.y == 0

    noun: Noun = get_component(combatant, Noun)
    assert noun.text == 'COMBATANT'

    attacker: Attacker = get_component(combatant, Attacker)
    assert attacker.strength == 12
