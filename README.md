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

```python
kinematics = world.create_query(
    all_of = [Position, Velocity],
    none_of = [IsFrozen],
)
```

```python
def process(dt):
    for entity in targets.result:
        entity[Position].x += entity[Velocity].x * dt
        entity[Position].y += entity[Velocity].y * dt
```

### Broadcasting Events to Components

```python
class Legs(pecs.Component):

    def on_try_move(self, evt: EntityEvent) -> None:
        pass        
```

## Notes & Ideas

- Create a context manager for a component's owning entity, similar to the way the Request object is used in Flask:


```python
from pecs import entity

class Legs(pecs.Component):

    def on_try_move(self, evt: EntityEvent) -> None:
        if self.is_blocked(*evt.data.target):
            if entity[Position].surrounding.is_interactable(*evt.data.target):
                entity.fire_event('try_interact', evt.data)
```

The `entity` object would get its specific value from the context of the method when it's called as part of event listening.
