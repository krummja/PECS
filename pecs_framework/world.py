from __future__ import annotations
from beartype.typing import *
from typing import TypeAlias
if TYPE_CHECKING:
    from pecs_framework.engine import Engine

from collections import OrderedDict


class World:
    
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._entities: OrderedDict[str, int] = OrderedDict()

