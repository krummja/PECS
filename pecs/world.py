from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs import Entity


class World:

    def create_entity(self) -> Entity:
        return Entity('<default>')
