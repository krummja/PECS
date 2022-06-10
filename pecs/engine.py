from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.component import Component, ComponentMeta


class Engine:

    def create_world(self):
        pass

    def register_component(self, component: ComponentMeta) -> None:
        pass

