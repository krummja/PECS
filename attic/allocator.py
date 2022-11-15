from __future__ import annotations
from beartype.typing import *
from typing import TypeAlias

from numpy.typing import DTypeLike, NDArray
import numpy as np
import numpy.ma as ma

from pecs_framework.component import Component

from rich.console import Console
from rich import inspect

c = Console()


class Allocator:
    
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
        comp_init = component.__init__
        annotations = comp_init.__annotations__
        del annotations['return']
        for var, annotation in annotations.items():
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
        tuple_vars = tuple(_ for _ in component_vars.values())
        return np.array([tuple_vars], dtype=dtype)

    def create_component_table(self, components: List[NDArray]) -> NDArray:
        return np.hstack(tuple(_ for _ in components))


class Position(Component):
    
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


allocator = Allocator()
allocator.register(Position)

ENTITIES = 100

components = []
for i in range(1, ENTITIES):
    position = Position(0, 0)
    position_arr = allocator.create_numpy_instance(position)
    components.append(position_arr)
    
positions = allocator.create_component_table(components)
c.print(positions)
c.print(positions.shape)  # (99,)
c.print(positions.ndim)   # 1

# Entities array denoting which component indices have the component.
entities = np.random.randint(low=0, high=2, size=(99,))
c.print(entities)

# Components table but masked via our entities array.
mask = ma.masked_array(positions, mask=(entities == 0))

def update_array(arr, update, mask):
    for i, _ in enumerate(arr):
        if mask[i] == arr[i]:
            arr[i] = arr[i] + update[i]
    return arr

update = np.full((99,), fill_value=1, dtype=positions.dtype)
c.print(update)

arr = update_array(positions, update, mask)
c.print(arr)
