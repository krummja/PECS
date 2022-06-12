from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.engine import Engine

from collections import OrderedDict

from pecs.component import Component, ComponentMeta


class ComponentRegistry:

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._cbit = 0
        self._map: OrderedDict[str, ComponentMeta] = OrderedDict()

    def register(self, component_class: ComponentMeta) -> None:
        component_class.cbit = self._cbit
        self._cbit += 1
        self._map[component_class.comp_id] = component_class

    def __getitem__(self, comp_id) -> ComponentMeta:
        return self._map[comp_id]


class ComponentLoader:

    def __init__(self) -> None:
        pass
