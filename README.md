# PECS
[![Tests](https://github.com/krummja/PECS/actions/workflows/main.yml/badge.svg)](https://github.com/krummja/PECS/actions/workflows/main.yml) [![Coverage Status](https://coveralls.io/repos/github/krummja/PECS/badge.svg?branch=master)](https://coveralls.io/github/krummja/PECS?branch=master)

![Armstrong](/assets/lm_pecs_armstrong.png)

PECS is the ✨Respectably Muscled✨ Python ECS library that aims to provide a powerful, user-friendly, and fast-as-hell framework for game development.

This library is the spiritual successor to my prior ECS library, [ECStremity](https://github.com/krummja/ECStremity). Both this and its predecessor were inspired by the JavaScript ECS library [geotic](https://github.com/ddmills/geotic), created and maintained by [@ddmills](https://github.com/ddmills). I highly recommend checking out that project as well as the excellent resources cited in its README.

What is ECS, you ask? [Check it out](https://medium.com/ingeniouslysimple/entities-components-and-systems-89c31464240d)!

## Installation

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
entity.add(IsFrozen())
```

### Component Initialization Patterns

Components can be initialized in a few different ways, depending on your preference:

#### Using `Entity.add` and a properties dict:
```python
zombie.add(Position, { 'x': 0, 'y': 123 })
```

#### Direct indexing with property dict assignment:
```python
hunter[Health] = { 'maximum': 300 }
```

#### Direct indexing with class instancing:
```python
yeti[IsFrozen] = IsFrozen()
```

### Queries

```python

```
