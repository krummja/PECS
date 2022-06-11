from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.component import ComponentMeta
    from pecs.entity import Entity
    from pecs.world import World

from functools import reduce
from pecs.helpers import *


class Query:
    _cache: List[Entity]

    def __init__(
            self,
            world: World,
            any_of: Optional[List[ComponentMeta]] = None,
            all_of: Optional[List[ComponentMeta]] = None,
            none_of: Optional[List[ComponentMeta]] = None,
        ) -> None:
        self._cache = []
        self._world = world

        self.any_of = any_of
        self.all_of = all_of
        self.none_of = none_of

        self._any = reduce(lambda a, b: add_bit(a, b.cbit), self.any_of, 0)
        self._all = reduce(lambda a, b: add_bit(a, b.cbit), self.all_of, 0)
        self._none = reduce(lambda a, b: add_bit(a, b.cbit), self.none_of, 0)

    @property
    def result(self):
        return self._cache

    def idx(self, entity: Entity) -> int:
        try:
            return self._cache.index(entity)
        except ValueError:
            return -1

    def matches(self, entity: Entity) -> bool:
        bits = entity.cbits
        any_of = self._any == 0 or bit_intersection(bits, self._any)
        all_of = bit_intersection(bits, self._all) == self._all
        none_of = bit_intersection(bits, self._none) == 0
        return any_of & all_of & none_of

    def candidate(self, entity: Entity) -> bool:
        idx = self.idx(entity)
        is_tracking = idx >= 0

        if self.matches(entity):
            if not is_tracking:
                self._cache.append(entity)
            return True

        if is_tracking:
            del self._cache[idx]
        return False

    def refresh(self) -> None:
        self._cache = []
        for entity in self.world.entities:
            self.candidate(entity)
