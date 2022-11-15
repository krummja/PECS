from __future__ import annotations
from beartype.typing import *
if TYPE_CHECKING:
    pass

from dataclasses import dataclass, field
import numpy as np
import numpy.ma as ma
from rich import inspect
from rich.console import Console
from rich.pretty import Pretty
from rich.panel import Panel

c = Console()


def subtract_bit(num: int, bit: int) -> int:
    return num & ~(1 << bit)


def add_bit(num: int, bit: int) -> int:
    return num | (1 << bit)


def has_bit(num: int, bit: int) -> bool:
    return (num >> bit) % 2 != 0


def bit_intersection(n1: int, n2: int) -> int:
    return n1 & n2


@dataclass
class Component:
    cbit: int = field(init=False)
    
    
class Entity:
    
    def __init__(self) -> None:
        self.cbits = 0
        self.components = OrderedDict()
    
    def add(self, component: Component) -> None:
        key = component.__class__.__name__.upper()
        self.components[key] = component
        self.cbits = add_bit(self.cbits, component.cbit)


@dataclass
class Position(Component):
    x: int
    y: int
    cbit: int = field(init=False, default=1)


@dataclass
class Velocity(Component):
    x: int
    y: int
    cbit: int = field(init=False, default=2)


@dataclass
class IsPlayer(Component):
    """Flag"""
    cbit: int = field(init=False, default=3)


e1 = Entity()
e2 = Entity()

e1.add(Position(10, 10))
e1.add(Velocity(0, 0))
e1.add(IsPlayer())

e2.add(Position(1, 1))
e2.add(Velocity(0, 1))

# Position      1
# Velocity      2
# IsPlayer      3

cbit = 0
cbit = add_bit(cbit, 1)
c.print(cbit)
# cbit = add_bit(cbit, 2)
# c.print(cbit)
cbit = add_bit(cbit, 3)
c.print(cbit)

# num | (1 << bit)
# (( 0 | (1 << 1)) | (1 << 3))               --> 10
# (((0 | (1 << 1)) | (1 << 2)) | (1 << 3))   --> 14

test = add_bit(add_bit(add_bit(0, 1), 2), 3)    # 14
c.print(test)

test2 = add_bit(add_bit(0, 1), 2)               # 10
c.print(test2)

test3 = add_bit(add_bit(0, 1), 3)               # 6
c.print(test3)

test4 = add_bit(add_bit(0, 2), 3)               # 12
c.print(test4)

# adding bits sequentially allows us to provide a unique signature for every
# possible combination of components
