from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.engine import Engine
    from pecs.query import Query, ComponentQuery

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
    def entities(self):
        return self._entities

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
        entity = Entity(self._engine, uid)
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

    def destroy(self):
        self.destroy_entities()
        self._world_id = 0
        self._queries = []
        self._entities = OrderedDict()

    def create_query(
            self,
            all_of: Optional[ComponentQuery] = None,
            any_of: Optional[ComponentQuery] = None,
            none_of: Optional[ComponentQuery] = None
        ) -> Query:
        query = Query(self, all_of, any_of, none_of)
        self._queries.append(query)
        return query

    def candidate(self, entity: Entity) -> None:
        for query in self._queries:
            query.candidate(entity)

    def create_prefab(self, name: str, properties: dict[str, Any], uid: str):
        properties = properties or {}
        return self._engine.prefabs.create(self, name, properties, uid)

    def serialize(self) -> str:
        pass

    def deserialize(self, world_data: str):
        pass

    def _deserialize_entity(self, entity_data: str):
        pass

    def _create_or_get_by_uid(self, uid: str):
        try:
            return self.get_entity(uid)
        except KeyError:
            return self.create_entity(uid)
