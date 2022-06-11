from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.engine import Engine
    from pecs.query import Query
    from collections.abc import ValuesView

from uuid import uuid1
from collections import OrderedDict

from pecs.entity import Entity
from pecs.query import Query


class World:

    @staticmethod
    def create_uid() -> str:
        return str(uuid1())

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

        self._world_id: int = 0
        self._queries: list[Query] = []
        self._entities: OrderedDict[str, Entity] = OrderedDict()

    @property
    def engine(self) -> Engine:
        """Reference to the Engine that this World is bound to."""
        return self._engine

    @property
    def entities(self) -> ValuesView[str, Entity]:
        return self._entities.values()

    def get_entity(self, uid: str) -> Entity | None:
        """Look up an Entity that currently exists in the World.

        :param uid:
            The unique string key identifying the Entity.
        :return:
            The Entity if it exists, None otherwise.
        """
        return self._entities.get(uid)

    def create_entity(self, uid: Optional[str] = None) -> Entity:
        """Create a new Entity.

        :param uid:
            An optional explicit unique string id to identify this Entity.
            This is useful for keeping a human-readable lookup key for
            specific Entities (e.g. the player).
        :return:
            The newly created Entity.
        """
        uid = uid or self.create_uid()
        entity = Entity(self, uid)
        self._entities[uid] = entity
        return entity

    def destroy_entity(self, uid: str) -> None:
        entity = self._entities[uid]
        if entity:
            entity.destroy()

    def destroy_entities(self) -> None:
        to_destroy = []
        for entity in self._entities:
            to_destroy.append(self.get_entity(entity))
        for entity in to_destroy:
            entity.destroy()

    def query(self) -> Query:
        return Query(self)

    def destroy(self):
        pass

    def create_query(self, any_of=None, all_of=None, none_of=None) -> Query:
        pass

    def candidate(self, entity: Entity) -> bool:
        pass

    def serialize(self):
        pass

    def deserialize(self, world_data: str):
        pass

    def _create_or_get_by_uid(self, uid: str):
        pass

    def _deserialize_entity(self, entity_data: str):
        pass
