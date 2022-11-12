from __future__ import annotations
from beartype.typing import *
from typing import TypeAlias
if TYPE_CHECKING:
    pass

from immutables import Map



m1 = Map(a=10, b=100)

print(m1)
print(m1['a'])

m2 = m1.set('a', 0)
print(m2)

m3 = m2.set('c', 50)
print(m3)
