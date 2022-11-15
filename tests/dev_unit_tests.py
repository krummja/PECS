from pecs_framework import Engine, Component
from dataclasses import dataclass

# Instantiate the ECS Engine.

ecs = Engine()


# Define a few component classes.

class Position(Component):  # <-- They are simple classes extending `Component`.
    
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Velocity(Component):
    
    def __init__(self, x: int, y: int) -> None:
        self.x = x  # <-- State classes have attributes.
        self.y = y

# We can define Components as dataclasses as well.

@dataclass
class Renderable(Component):
    ch: str
    fg: tuple[int, int, int]
    bg: tuple[int, int, int]

# Flag Components can be created by making empty classes. These simply represent
# atomic boolean attributes.

class IsPlayer(Component):
    """Flag"""


# Register the component classes with the ECS Engine.

ecs.components.register(Position)
ecs.components.register(Velocity)
ecs.components.register(Renderable)
ecs.components.register(IsPlayer)

domain = ecs.current_domain

# Now we can make a couple of entities.

e1 = domain.create_entity()
# Use an alias for easier lookup.
e2 = domain.create_entity(alias='entity 2')
e3 = domain.create_entity(alias='player')


# Now we can attach component instances to our entities.

ecs.attach_component_type(e1, Position, {'x': 10, 'y': 0})
ecs.attach_component(e2, ecs.get_component('position')(10, 10))
ecs.attach_component(e3, ecs.get_component('Position')(1, 1))
ecs.attach_component(e1, Renderable('@', (255, 0, 255), (0, 0, 0)))
ecs.attach_component(e3, Velocity(0, 0))

velocity = ecs.get_component('Velocity')
ecs.attach_component(e3, velocity(1, 1))
ecs.attach_component(e3, ecs.get_component('IsPlayer')())


#! TESTS ======================================================================

def test_entity_creation():
    """
    Test that the Entity instances we created exist and are accessible via the
    aliases we defined.
    """
    assert domain.get_entity_by_alias('entity 2') is not None
    assert domain.get_entity_by_alias('player') is not None


def test_component_registration():
    """
    Test that specific Component types exist in the ECS Engine and that their 
    cbit values are what we expect.
    """
    position = ecs.get_component('Position')
    velocity = ecs.get_component('Velocity')
    is_player = ecs.get_component('IsPlayer')
    
    assert position.cbits == 1
    assert velocity.cbits == 2
    assert is_player.cbits == 4


def test_component_attachment():
    """
    Test that our Component attachments were successful by checking that the
    Entities' cbit states correspond to what is expected for the Entity Type.
    """
    entity = domain.get_entity_by_alias('entity 2')
    player = domain.get_entity_by_alias('player')
    
    # We've only attached a single component, Position, with a __cbits__ value
    # of 1. This means our expected __cbits__ after attachment is the result of
    # (entity.__cbits__ | (component.__cbits__ << 1))
    
    # entity.__cbits__ = 1
    # component.__cbits__ = 1
    # (0 | (1 << 1)) = 2
    assert entity.cbits == 2

    # If perform the same test against the 'player' entity, we should get a 
    # value of 14, since it has all three components attach to it.
    
    # (((0 | (1 << 1)) | (1 << 2)) | (1 << 3)) = 14
    assert player.cbits == 22
