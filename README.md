## PECS

```python
import pecs

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
        
        
class Health(pecs.Component):
    """Representation of an Entity's health."""
    
    def __init__(self, maximum: int) -> None:
        self.maximum = maximum
        self.current = maximum


class IsFrozen(pecs.Component):
    """Flag component denoting a frozen Entity."""


engine = pecs.Engine()

engine.register_component(Position)
engine.register_component(Velocity)
engine.register_component(IsFrozen)

world = engine.create_world()

entity = world.create_entity()

entity.add(Position, { 'x': 10, 'y': -2 })
entity[Velocity] = Velocity(10, 100)

# TODO Implement this style of initialization
entity[Health] = { 'maximum': 300 }
```
