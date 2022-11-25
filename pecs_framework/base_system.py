from __future__ import annotations
from beartype.typing import *
from typing import TypeAlias
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from pecs_framework.query import Query, ComponentQuery
    from pecs_framework.domain import Domain
    from pecs_framework.engine import Engine


class Loop(ABC):

    def __init__(self, ecs: Engine, domain: Domain) -> None:
        self.ecs = ecs
        self.domain = domain
        self.initialize()

    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError("Method has no implementation")

    @abstractmethod
    def teardown(self) -> None:
        raise NotImplementedError("Method has no implementation")

    @abstractmethod
    def pre_update(self) -> None:
        raise NotImplementedError("Method has no implementation")

    @abstractmethod    
    def update(self) -> None:
        raise NotImplementedError("Method has no implementation")

    @abstractmethod
    def post_update(self) -> None:
        raise NotImplementedError("Method has no implementation")


class BaseSystem:

    def __init__(self, loop: Loop) -> None:
        self.loop = loop
        self._queries: dict[str, Query] = {}
        self.initialize()

    def query(
            self, 
            key: str, 
            all_of: ComponentQuery | None = None,
            any_of: ComponentQuery | None = None, 
            none_of: ComponentQuery | None = None,
        ) -> None:
        all_of = all_of if all_of else []
        any_of = any_of if any_of else []
        none_of = none_of if none_of else []
        self._queries[key] = self.loop.domain.create_query(
            all_of, 
            any_of, 
            none_of,
        )

    def initialize(self):
        raise NotImplementedError("Method has no implementation")

    def update(self):
        raise NotImplementedError("Method has no implementation")
