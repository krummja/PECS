from __future__ import annotations
from beartype.typing import TYPE_CHECKING
from beartype.typing import Sequence
from beartype.typing import Any
from typing import TypeAlias

if TYPE_CHECKING:
    from pecs_framework.entities import Entity
    from pecs_framework.domain import Domain

from functools import reduce

from pecs_framework.component import ComponentMeta
from pecs_framework.utils import add_bit
from pecs_framework.utils import bit_intersection


ComponentQuery: TypeAlias = list[ComponentMeta]


class Query:

    def __init__(
        self,
        domain: Domain,
        all_of: ComponentQuery | None = None,
        any_of: ComponentQuery | None = None,
        none_of: ComponentQuery | None = None,
    ) -> None:
        self._domain = domain

        all_of = all_of if all_of is not None else []
        any_of = any_of if any_of is not None else []
        none_of = none_of if none_of is not None else []

        self._all = reduce(lambda a, b: add_bit(a, b.cbit), all_of, 0)
        self._any = reduce(lambda a, b: add_bit(a, b.cbit), any_of, 0)
        self._none = reduce(lambda a, b: add_bit(a, b.cbit), none_of, 0)

        self._cache: list[Entity] = []
        self._indices: dict[Entity, int] = {}
        self.refresh()

    @property
    def result(self) -> Sequence[Entity]:
        return self._cache

    def index(self, entity: Entity) -> int:
        return self._indices.get(entity, -1)

    def matches(self, entity: Entity) -> bool:
        bits = entity.cbits
        all_of = bit_intersection(bits, self._all) == self._all
        any_of = self._any == 0 or bool(bit_intersection(bits, self._any))
        none_of = bit_intersection(bits, self._none) == 0
        return any_of & all_of & none_of

    def candidate(self, entity: Entity) -> bool:
        index = self.index(entity)
        is_tracking = index >= 0

        if self.matches(entity):
            if not is_tracking:
                self._cache.append(entity)
                self._indices[entity] = len(self._cache) - 1
            return True

        if is_tracking:
            del self._cache[index]
            self.build_indices()
        return False

    def refresh(self) -> None:
        self._cache = []
        for entity in self._domain.entities.values():
            self.candidate(entity)

    def build_indices(self) -> None:
        self._indices = dict(zip(self._cache, range(0, len(self._cache))))
