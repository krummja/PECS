# PECS
[![Tests](https://github.com/krummja/PECS/actions/workflows/main.yml/badge.svg)](https://github.com/krummja/PECS/actions/workflows/main.yml) [![Coverage Status](https://coveralls.io/repos/github/krummja/PECS/badge.svg?branch=master)](https://coveralls.io/github/krummja/PECS?branch=master)

![Armstrong](/static/lm_pecs_armstrong.png)

PECS is the ✨Respectably Muscled✨ Python ECS library that aims to provide a powerful, user-friendly, and fast-as-hell framework for game development.

This library is the spiritual successor to my prior ECS library, [ECStremity](https://github.com/krummja/ECStremity). Both this and its predecessor were inspired by the JavaScript ECS library [geotic](https://github.com/ddmills/geotic), created and maintained by [@ddmills](https://github.com/ddmills). I highly recommend checking out that project as well as the excellent resources cited in its README.

What is ECS, you ask? [Check it out](https://medium.com/ingeniouslysimple/entities-components-and-systems-89c31464240d)!

## Installation

Install the package from PyPI using pip:

```
pip install pecs-framework
```

Or grab it directly from this repository:

```
pip install git+https://github.com/krummja/PECS
```

## Usage and Examples

To start flexing your PECS, import the library and set up some components. Components can be built as standard Python classes:

```python
import pecs_framework as pecs


class Position(pecs.Component):
    """Representation of an Entity's position in 2D space."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    @property
    def xy(self) -> tuple[int, int]:
        return self.x, self.y
```

As extensions of existing components:

```py
import pecs_framework as pecs


class Velocity(Position):
    """Representation of an Entity's velocity in 2D space."""

```

Or as dataclasses:

```py
import pecs_framework as pecs
from dataclasses import dataclass, field


@dataclass
class Health(pecs.Component):
    """Representation of an Entity's health."""
    maximum: int = 100
    current: int = field(init=False)

    def __post_init__(self) -> None:
        self.current = self.maximum
```

Components can have as much or as little behavior as needed, although it is generally better to keep to a strict single-repsonsibility principle. We can even have components that have no behavior at all, representing boolean flags for queries:

```py
import pecs_framework as pecs


class IsFrozen(pecs.Component):
    """Flag component denoting a frozen entity."""
```


### Queries

The easiest way to build out systems is through world queries. To make a system that tracks and updates the components relevant to movement, we might query for `Position` and `Velocity` components. Because we want our entities to move, we want to exclude those marked with the `IsFrozen` flag. Perhaps we also want to grab only those entities that can fly through `Wings` or swim through `Fins`: 

```python
import pecs_framework as pecs


ecs = pecs.Engine()
domain = ecs.create_domain("World")

kinematics = domain.create_query(
    all_of = [
        Position, 
        Velocity
    ],
    any_of = [
        Wings, 
        Fins
    ],
    none_of = [
        IsFrozen
    ],
)
```

Queries can specify `all_of`, `any_of`, or `none_of` quantifiers. The query in the example above asks for entities that must have **both** `Position` **and** `Velocity`, may have (inclusive) `Wings` **or** `Fins`, and **must not** have `IsFrozen`.

We can access the result set of the query and do some operation on them every loop cycle:

```py
def process(dt):
    for entity in targets.result:
        entity[Position].x += entity[Velocity].x * dt
        entity[Position].y += entity[Velocity].y * dt
```

For convenience, the library provides barebones system class that you can extend for your own purposes:

```py
import pecs_framework as pecs


class MovementSystem(pecs.BaseSystem):

    def initialize(self) -> None:
        self.query(
            'movable',
            all_of = [Position, Velocity],
            none_of = [IsFrozen],
        )

    def update(self) -> None:
        movables = self._queries
```

> ---
> 
> **Warning:** 
> 
> Do not override the `__init__` method of `BaseSystem` -- use the provided `initialize` method instead.
> 
> --- 


### Broadcasting Events to Components

Complex interactions within and among entities can be achieved by firing events on an entity. This creates an `EntityEvent` that looks for methods on all of the entity's methods prefixed with `on_`.

```python
zombie.fire_event('attack', {
    'target': survivor,
    'multiplier': 1.5,
})
```

On the `zombie` entity, we might have attached an `Attacker` component with the following logic:

```python
class Attacker(pecs.Component):

    def __init__(self, strength: int) -> None:
        self.strength = strength

    def on_attack(self, evt: pecs.EntityEvent) -> pecs.EntityEvent:
        target: Entity = evt.data.target
        target.fire_event('damage_taken', {
            'amount': self.strength * evt.data.pultiplier,
        })
        evt.handle()
        return evt
```

When we execute `fire_event` with the event name `attack`, the event system will find all `on_attack` methods on that entity's components. If we want the event propagation to stop at a particular component, we can call `evt.handle()` which will immediately break broadcasting down the component list. This means that we can potentially have any number of components respond to a specific event, although it may generally be safer to fire a secondary event to prevent ordering issues.

Internally, the `EntityEvent` class puts together an instance of the class `EventData`, which provides access to the properties defined in the `fire_event` call.

```python
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

### Creating Entities from Prefabs

PECS supports defining prefab entities with preconfigured component properties. Define prefabs as `.json` files and register them with the engine:

```json
{
  "name": "GameObject",
  "inherit": [],
  "components": [
    {
      "type": "Position"
    },
    {
      "type": "Renderable",
      "properties": {
        "ch": "?",
        "bg": [0, 0, 0],
      }
    },
    {
      "type": "Noun"
    }
  ]
}
```

```py
import pecs_framework as pecs
import os


ROOTDIR = os.path.dirname(__file__)
PREFABS = os.path.join(ROOTDIR, 'prefabs')


ecs = pecs.Engine()
ecs.prefabs.register(PREFABS, 'game_object')
```

Now PECS will look for a file named `game_object.json` in the specified prefabs path and automatically load it for you. We can build an entity using this prefab very easily:

```py
game_object = ecs.domain.entities.create_from_prefab(
    template = 'GameObject',
    properties = {
        'Position': {
            'x': 15,
            'y': 10,
        },
        'Renderable': {
            'fg': [255, 0, 255],
        },
        'Noun': {
            'text': 'Test Object'
        }
    },
    alias = 'test_object_01',
)
```

Prefabs can specify other prefabs to inherit from as well. Prefabs can be defined as hierarchies of any depth and breadth. Note that properties will always be resolved from the most deeply embedded prefab to the least, overwriting with the most recent specification. If no properties are passed in the prefab or when creating from prefab, defaults from the component itself will be used.

For examples, check out the `tests` folder in this repository.
