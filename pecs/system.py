from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.engine import Engine
    from pecs.query import Query, ComponentQuery


class System:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.queries: dict[str, Query] = {}
        self.initialize()

    def query(
            self,
            key: str,
            all_of: Optional[ComponentQuery] = None,
            any_of: Optional[ComponentQuery] =None,
            none_of: Optional[ComponentQuery] = None,
        ) -> None:
        self.queries[key] = self.engine.world.create_query(all_of, any_of, none_of)

    def initialize(self):
        raise NotImplementedError

    def update(self, dt: float = 0.0):
        raise NotImplementedError
