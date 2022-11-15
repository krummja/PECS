---
id: 5kctzq8mfx7tjjr847sknbx
title: Numpy
desc: ''
updated: 1668370684462
created: 1668369298013
---

I want the interface to look something like the following:

```py
ecs = Engine()

@ecs.component
class Position:
    """Entity's world position."""
    x: int
    y: int

@ecs.component
class Velocity:
    """Entity's world velocity."""
    x: int
    y: int

@ecs.component
class IsPlayer:
    """Flag component representing the Player entity."""


ecs.create_entity(alias='player')
ecs.attach_component(alias='player', Position(10, 10))
ecs.attach_component(alias='player', Velocity(0, 0))
ecs.attach_component(alias='player', IsPlayer())
```

Underlyingly, the ECS will abstract the components and entities out to numpy arrays for extremely fast operations and indexing.

```py
import numpy as np


```
