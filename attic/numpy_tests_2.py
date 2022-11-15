from __future__ import annotations
from beartype.typing import *
from typing import TypeAlias, Annotated
if TYPE_CHECKING:
    from numpy.typing import ArrayLike, DTypeLike, NDArray

from abc import abstractmethod, ABC
from beartype import beartype
from beartype.vale import Is
from beartype.door import is_bearable, die_if_unbearable
from immutables import Map

import attr
import numpy as np
from dataclasses import dataclass

from rich.console import Console
from rich.pretty import Pretty
from rich import inspect

c = Console()


position = np.dtype([
    ('id', '<i8'),
    ('x', '<i8'),
    ('y', '<i8'),
    ('z', '<i8'),
])


velocity = np.dtype([
    ('id', '<i8'),
    ('x', '<i8'),
    ('y', '<i8'),
    ('z', '<i8'),
])


positions = np.array([
    (1, 0, 0, 0),
    (2, 0, 1, 0),
    (3, 1, 30, 2),
], dtype=position)


velocities = np.array([
    (1, 1, 1, 0),
    (2, 0, 0, 0),
    (3, 2, 1, 0),
], dtype=velocity)


velocities_shape = velocities.shape
r_velocities = np.ravel(velocities)
u_velocities = np.reshape(r_velocities, velocities_shape)
c.print(r_velocities)
c.print(u_velocities)

positions_shape = positions.shape
r_positions = np.ravel(positions)
u_positions = np.reshape(r_positions, positions.shape)


test = np.hstack((r_velocities, r_positions))
c.print(test)

# number of components, number of fields
c.print(np.reshape(test, (2, 3)))

c_positions = np.ascontiguousarray(positions)
c.print(c_positions)


@dataclass
class Component:
    pass


@dataclass
class Position:
    x: int
    y: int
    z: int
    
    
@dataclass
class Entity:
    cbits: ClassVar[int]
    uid: int
    

class ComponentRegistry:
    
    def __init__(self) -> None:
        self._map = {}
        self.type_map = {
            'int': np.int64,
        }
        
    def register(self, component: Type[Component]) -> None:
        """Add a component accessor to the registry."""
        _mapping = self._map_annotations(component)
        self._map[component.__name__.upper()] = _mapping

    def _map_annotations(self, component: Type[Component]):
        """Add a component's fields and their types to internal mapping."""
        mapping = []
        for var, annotation in component.__annotations__.items():
            mapping.append((var, self.type_map[annotation]))
        return mapping
    
    def create_dtype(self, component_name: str) -> DTypeLike:
        """Create a numpy dtype from a registered component."""
        annotations = self._map[component_name.upper()]
        _dtype = np.dtype(annotations)
        return _dtype
    
    def create_numpy_instance(self, component: Component) -> NDArray:
        """Instantiate a new NDArray from a component instance."""
        dtype = self.create_dtype(component.__class__.__name__)
        component_vars = vars(component)
        return np.array([_ for _ in component_vars.values()], dtype=dtype)
        

registry = ComponentRegistry()
registry.register(Position)
c.print(registry._map)

inspect(Position)
registry.create_dtype('position')

c.print(vars(Position(10, 10, 0)))

arr = registry.create_numpy_instance(Position(10, 10, 0))
c.print(arr)
c.print(arr.shape)
c.print(arr.dtype)
