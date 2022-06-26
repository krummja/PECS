# PECS
[![Tests](https://github.com/krummja/PECS/actions/workflows/main.yml/badge.svg)](https://github.com/krummja/PECS/actions/workflows/main.yml) [![Coverage Status](https://coveralls.io/repos/github/krummja/PECS/badge.svg?branch=master)](https://coveralls.io/github/krummja/PECS?branch=master)

![Armstrong](/static/lm_pecs_armstrong.png)

PECS is the ✨Respectably Muscled✨ Python ECS library that aims to provide a powerful, user-friendly, and fast-as-hell framework for game development.

| :warning: PROJECT IN DEVELOPMENT                                                               |
|:-----------------------------------------------------------------------------------------------|
| This project is still in development, and as such its API is subject to change without notice. |

This library is the spiritual successor to my prior ECS library, [ECStremity](https://github.com/krummja/ECStremity). Both this and its predecessor were inspired by the JavaScript ECS library [geotic](https://github.com/ddmills/geotic), created and maintained by [@ddmills](https://github.com/ddmills). I highly recommend checking out that project as well as the excellent resources cited in its README.

What is ECS, you ask? [Check it out](https://medium.com/ingeniouslysimple/entities-components-and-systems-89c31464240d)!

## Installation

| :exclamation: This package is not yet published on PyPI! |
|----------------------------------------------------------|

```
pip install pecs-framework
```

## Usage and Examples

To start flexing your PECS, import the library and set up some components.

```python
import pecs


class Position(pecs.Component):
    """Representation of an Entity's position in 2D space."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
        
        
class Velocity(pecs.Component):
    """Representation of an Entity's velocity in 2D space."""
    
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
        
        
class Health(pecs.Component):
    """Representation of an Entity's health."""
    
    def __init__(self, maximum: int) -> None:
        self.maximum = maximum
        self.current = maximum  
        
        
class IsFrozen(pecs.Component):
    """Flag Component denoting a frozen Entity."""


ecs = pecs.Engine()

# All Component and Prefab classes must be registered with the engine.
ecs.register_component(Position)
ecs.register_component(Health)
ecs.register_component(IsFrozen)

# Create a World to hold and create entities and queries.
world = ecs.create_world()

# We can then ask the World instance to create Entity instances for us.
entity = world.create_entity()

# Finally, we can add components to our newly created Entity.
entity.add(Position, { 'x': 10, 'y': -2 })
entity.add(Health, { 'maximum': 100 })
entity.add(IsFrozen)
```

### Queries

The easiest way to build out systems is through world queries. To make a system that tracks and updates the components relevant to movement, we might query for `Position` and `Velocity` components. Because we want our entities to move, we want to exclude those marked with the `IsFrozen` flag. Perhaps we also want to grab only those entities that can fly through `Wings` or swim through `Fins`: 

```python
kinematics = world.create_query(
     all_of = [Position, Velocity],
     any_of = [Wings, Fins],
    none_of = [IsFrozen],
)
```

Queries can specify `all_of`, `any_of`, or `none_of` quantifiers. The query in the example above asks for entities that must have **both** `Position` **and** `Velocity`, may have **either** `Wings` **or** `Fins`, and **must not** have `IsFrozen`.

We can access the result set of the query and do some operation on them every loop cycle:

```python
def process(dt):
    for entity in targets.result:
        entity[Position].x += entity[Velocity].x * dt
        entity[Position].y += entity[Velocity].y * dt
```

### Broadcasting Events to Components

Complex interactions within and among entities can be achieved by firing events on an entity. This creates an `EntityEvent` that looks for methods on all of the entity's methods prefixed with `on_`.

```python
zombie.fire_event('attack', {
    'target': survivor,
    'multiplier': 1.5
})
```

On the `zombie` entity, we might have attached an `Attacker` component with the following logic:

```python
class Attacker(pecs.Component):

    def __init__(self, strength: int) -> None:
        self.strength = strength

    def on_attack(self, evt: pecs.EntityEvent) -> pecs.EntityEvent:
        target = evt.data.target
        target.fire_event('damage_taken', {
            'amount': self.strength * evt.data.multiplier
        })
        evt.handle()
```

When we execute `fire_event` with the event name `attack`, the event system will find all `on_attack` methods on that entity's components. If we want the event propagation to stop at a particular component, we can call `evt.handle()` which will immediately break broadcasting down the component list.  

Internally, the `EntityEvent` class puts together an instance of the class `EventData`, which provides access to the properties defined in the `fire_event` call.

```python
import pecs

zombie.fire_event('attack', {
    'target': survivor,                 # <-- We defined 'target' here
    'multiplier': 1.5                   # <-- and 'multiplier' here
})

def on_attack(self, evt: pecs.EntityEvent) -> pecs.EntityEvent:
    target = evt.data.target            # --> survivor
    multiplier = evt.data.multiplier    # --> 1.5
```

Actions can also be defined as a tuple and passed into the `fire_event` method. This allows for easy abstraction over variables used in the event:

```python
attack_against = (lambda target : ('attack', {
    'target': target,
    'multiplier': 1.5
}))

zombie.fire_event(attack_against(survivor))
```
