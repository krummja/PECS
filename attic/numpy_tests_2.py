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

from rich.console import Console


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
])

import numpy.ma as ma

m_velocities = ma.masked_array(velocities, mask=[0, 1, 1])

c.print(m_velocities)
