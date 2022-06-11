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
        self._map: OrderedDict[str, Component] = OrderedDict()

    def register(self, component_class: ComponentMeta) -> None:
        pass

    def __getitem__(self, component_class: ComponentMeta) -> Component:
        pass
