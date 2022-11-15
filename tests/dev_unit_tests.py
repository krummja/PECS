from pecs_framework import Engine, Component


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

class IsPlayer(Component):
    """Flag"""      # <-- Flag classes are empty.


# Register the component classes with the ECS Engine.

ecs.components.register(Position)
ecs.components.register(Velocity)
ecs.components.register(IsPlayer)


# Now we can make a couple of entities.

e1 = ecs.domain.create_entity()
e2 = ecs.domain.create_entity(alias='entity 2')  # <-- Use an alias for easier lookup.
e3 = ecs.domain.create_entity(alias='player')


# Now we can attach component instances to our entities.

ecs.attach_component_type(e1, Position, {'x': 10, 'y': 0})
ecs.attach_component(e2, ecs.get_component('position')(10, 10))
ecs.attach_component(e3, ecs.get_component('Position')(1, 1))
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
    assert ecs.domain.get_entity_by_alias('entity 2') is not None
    assert ecs.domain.get_entity_by_alias('player') is not None


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
    assert is_player.cbits == 3


def test_component_attachment():
    """
    Test that our Component attachments were successful by checking that the
    Entities' cbit states correspond to what is expected for the Entity Type.
    """
    entity = ecs.domain.get_entity_by_alias('entity 2')
    player = ecs.domain.get_entity_by_alias('player')
    
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
    assert player.cbits == 14
