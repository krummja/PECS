from __future__ import annotations
from beartype.typing import *
from typing import TypeAlias, Annotated
if TYPE_CHECKING:
    from numpy.typing import ArrayLike, DTypeLike

from abc import abstractmethod, ABC
from beartype import beartype
from beartype.vale import Is
from beartype.door import is_bearable, die_if_unbearable
from immutables import Map

import attr
import numpy as np
from dataclasses import dataclass

"""
Instead of concrete classes being stateful components, treat components as transient delegates that manipulate an underlying table that stores the actual state values.
"""


class AbstractComponent(ABC):
    
    @abstractmethod
    def __iter__(self):
        while False:
            yield None
    
    def get_iterator(self):
        return self.__iter__()
    
    @classmethod
    def __subclasshook__(cls, other: Any) -> bool:
        if cls is AbstractComponent:
            if any("__iter__" in B.__dict__ for B in other.__mro__):
                return True
        return NotImplemented


Component = Annotated[type, Is[lambda cls: hasattr(cls, "__component_id__")]]
IdStr = Annotated[str, Is[lambda id_str: id_str == id_str.upper()]]


class ComponentRegistry:
    
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._cbit = 0
        self._map: Map[IdStr, Component] = Map()
        
    @beartype
    def _register(self, key: IdStr, value: Component) -> None:
        new_map = self._map.set(key, value)
        self._map = new_map
        self._cbit += 1
        
    def get(
            self, 
            key: str | Component, 
            configuration: dict[str, Any] | None = None
        ) -> Component:
        if isinstance(key, str):
            _key: IdStr = key.upper()
            component = self._map[_key]
        else:
            clsname = key.__name__.upper()
            component = self._map[clsname]
            
        die_if_unbearable(component, Component)
        if configuration is not None:
            component = component(**configuration)
            
        return component


class Domain:
    
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        

class Engine:
    
    def __init__(self) -> None:
        self._domain = Domain(self)
        self._components = ComponentRegistry(self)
        self._states: dict[str, Any] = {}

    @property
    def domain(self) -> Domain:
        return self._domain
    
    @property
    def components(self) -> ComponentRegistry:
        return self._components

    @beartype
    def component(self, cls: Any = None) -> Component:
        cls = dataclass(cls)
        clsname: IdStr = cls.__name__.upper()
        setattr(cls, '__component_id__', clsname)
        self.components._register(clsname, cls)
        return cls


class Entity:
    
    def __init__(self, uid: str) -> None:
        self._uid = uid
        self.cbit = 0
        
    def __repr__(self) -> str:
        cbit = str(bin(self.cbit)).replace('0b', '')
        if self.cbit < 32:
            cbit = cbit.rjust(4, '0')
        if self.cbit >= 32:
            cbit = (cbit[-8:-4] + ' ' + cbit[-4:]).rjust(9, '0')
        return f'<Entity: {self._uid} [{cbit}][{self.cbit}]>'


ecs = Engine()


@ecs.component
class Position:
    x: int = 0
    y: int = 0
    
    @property
    def xy(self) -> tuple[int, int]:
        return self.x, self.y


class Velocity:
    x: int = 0
    y: int = 0


class IsFrozen:
    """Flag class denoting an entity that is frozen."""


def subtract_bit(num: int, bit: int) -> int:
    return num & ~(1 << bit)

def add_bit(num: int, bit: int) -> int:
    return num | (1 << bit)

def has_bit(num: int, bit: int) -> bool:
    return (num >> bit) % 2 != 0

def bit_intersection(n1: int, n2: int) -> int:
    return n1 & n2


if __name__ == '__main__':
    from rich.console import Console
    c = Console()
    
    p1 = ecs.components.get('position')(x=100, y=20)
    p2 = ecs.components.get(Position)(x=10, y=20)
    p3 = ecs.components.get(Position, {'x': 10, 'y': 20})

    ecs.component(Velocity)
    v1 = ecs.components.get(Velocity, {'x': 10, 'y': 10})

    c.print(p1)
    c.print(p2)
    c.print(p3)
    c.print(v1)
    
    import numpy.ma as ma
    
    x = np.array([0, 1, 0, 1, 1, 0, 1])
    y = np.array([0, 1, 1, 0, 1, 1, 1])
    mx = ma.masked_array(x, mask=[0, 1, 1, 1, 0, 1, 0])
    
    c.print(x)
    c.print(y)
    c.print(np.bitwise_and(x, y))

    b1 = 2
    b2 = 5
    
    c.print(b2)
    c.print(add_bit(b1, b2))
    
    
    def add_component(entity: Entity, component: int) -> Entity:
        entity.cbit = add_bit(component, entity.cbit)
        return entity
    
    e1 = Entity('A')
    e2 = Entity('B')
    
    e1 = add_component(e1, 1)
    e1 = add_component(e1, 2)
    e1 = add_component(e1, 3)
    
    e2 = add_component(e2, 2)
    e2 = add_component(e2, 3)

    c.print(e1)
    c.print(e2)
    
    c.print(has_bit(0b1010, 2))

    
    class PositionArr:
        
        def __init__(self) -> None:
            self._array = np.array([0, 1, 2, 3], dtype=self.dtype)
            self._shape = self._array.shape
        
        def add(self, id: int, pos: tuple[int, int, int]) -> None:
            np.append(
                self._array, 
                np.array([[id, pos[0], pos[1], pos[2]]]), 
                axis=0
            )
        
        @property
        def dtype(self) -> DTypeLike:
            return np.dtype([
                ('id', '<i8'),
                ('x', '<i8'),
                ('y', '<i8'),
                ('z', '<i8'),
            ])
        
        def __repr__(self) -> str:
            return f'<Position: {self.dtype}>'
        

    n1 = np.array([[1, 2, 3]])
    n2 = np.append(n1, np.array([[4, 5, 6]]), axis=0)
    c.print(n2)

    # p1 = PositionArr()
    # c.print(p1._array)
    # p1.add(id=1, pos=(1, 2, 3))
    # c.print(p1._array)
    # c.print(p1)

    pos_type = np.dtype([
        ('id', '<i8'),
        ('x', '<i8'),
        ('y', '<i8'),
        ('z', '<i8'),
    ])
    
    n3 = np.array([(1, 2, 3, 4), (2, 0, 0, 1)], dtype=pos_type)
    
    id_iter = n3['id']
    c.print(n3[1:2])
    
    # [0:1]   ___________
    #       [(1, 2, 3, 4), (2, 0, 0, 1)]
    
    # [1:2]                 ___________
    #       [(1, 2, 3, 4), (2, 0, 0, 1)]
    
    n3['x'] += 2   # broadcasted addition to the 'x' field
    c.print(n3[['x', 'y']])   # strutured indexing of ('x', 'y') tuples
    c.print(n3)
    