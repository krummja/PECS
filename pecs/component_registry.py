from __future__ import annotations
from typing import *

from collections import OrderedDict

from pecs.component import Component


class ComponentRegistry:

    def __init__(self) -> None:
        self._cbit = 0
        self._map: OrderedDict[str, Component] = OrderedDict()

    def register(self, component: Component) -> None:
        pass

