from __future__ import annotations
from beartype import beartype
from beartype.typing import *
from beartype.vale import Is
from typing import TypeAlias, Annotated
if TYPE_CHECKING:
    pass

from dataclasses import dataclass
from collections import OrderedDict


Component = Annotated[type, Is[lambda cls: hasattr(cls, '__component_id__')]]
IdStr = Annotated[str, Is[lambda id_str: id_str == id_str.upper()]]


class ComponentRegistry:
    
    def __init__(self) -> None:
        self._cbit = 0
        self._map: OrderedDict[IdStr, Component] = OrderedDict()
        
    @beartype
    def register(self, key: IdStr, value: Component) -> None:
        self._map[key] = value
        self._cbit += 1


class Engine:
    
    def __int__(self) -> None:
        pass
    
    
    