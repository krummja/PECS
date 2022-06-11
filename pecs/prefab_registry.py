from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.engine import Engine
    from pecs.entity import Entity
    from pecs.world import World

from pecs.prefab import Prefab
from pecs.prefab_component import PrefabComponent


class PrefabRegistry:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def register(self, data: Dict[str, Any]) -> None:
        pass

    def deserialize(self, data: str) -> Prefab:
        pass

    def create(
            self, 
            world: World,
            name: str,
            properties: Optional[Dict[str, Any]] = None,
            uid: Optional[str] = None
        ) -> Entity:
        pass

    def clear(self) -> None:
        pass

    def get(self, name: str) -> Prefab:
        pass

