from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.entity import Entity
    from pecs.world import World

from functools import reduce

from pecs.component import ComponentMeta
from pecs.helpers import *


ComponentQuery = list[ComponentMeta]


class Query:
    _cache: List[Entity]

    def __init__(
            self,
            world: World,
            all_of: Optional[ComponentQuery] = None,
            any_of: Optional[ComponentQuery] = None,
            none_of: Optional[ComponentQuery] = None,
        ) -> None:
        self._cache = []
        self._world = world
        self._all = reduce(lambda a, b: add_bit(a, b.cbit), all_of or [], 0)
        self._any = reduce(lambda a, b: add_bit(a, b.cbit), any_of or [], 0)
        self._none = reduce(lambda a, b: add_bit(a, b.cbit), none_of or [], 0)
        self.refresh()

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
        all_of = bit_intersection(bits, self._all) == self._all
        any_of = self._any == 0 or bit_intersection(bits, self._any)
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
        for _, entity in self._world.entities.items():
            self.candidate(entity)
