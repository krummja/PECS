from __future__ import annotations
from beartype.typing import *

from uuid import uuid1
from collections import OrderedDict

if TYPE_CHECKING:
    from pecs_framework._types import IdStr
    from pecs_framework.engine import Engine, CInst
    from pecs_framework.component import Component
    
from pecs_framework.entity import Entity


class Domain:
    
    @staticmethod
    def create_uid() -> str:
        return str(uuid1())
    
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.entities: dict[IdStr, Entity] = OrderedDict()
        self.queries = OrderedDict()
        self.aliases = OrderedDict()
    
    def get_entity_id(self, entity_or_alias: Entity | str) -> str:
        """
        Get an Entity's identifier either by passing the entity itself or its
        alias.

        Parameters
        ----------
        entity_or_alias
            An Entity instance or a string alias to an Entity

        Returns
        -------
            The Entity's unique identifier
        """
        if isinstance(entity_or_alias, str):
            id_: str = self.aliases.get(entity_or_alias, '')
        else:
            id_: str = entity_or_alias.eid
        return id_
    
    def get_cbits(self, entity_or_alias: Entity | str) -> int:
        """
        Get the cbits for a specific Entity.

        Parameters
        ----------
        entity_or_alias
            An Entity instance or a string alias to an Entity

        Returns
        -------
            The cbit state of the target Entity
        """
        if isinstance(entity_or_alias, str):
            return self.get_entity_by_alias(entity_or_alias).cbits
        return entity_or_alias.cbits
    
    def create_entity(self, alias: str | None = None) -> Entity:
        """
        Create a new Entity in the engine's Entity registry.

        Parameters
        ----------
        alias, optional
            Optional alias for easy entity lookup, by default None

        Returns
        -------
            The newly created Entity instance
        """
        entity = Entity(self.create_uid())
        self.entities[entity.eid] = entity
        
        if alias:
            self.aliases[alias] = entity.eid
            
        return entity

    def get_entity_by_alias(self, alias: str) -> Entity:
        """
        Get a specific Entity instance via its alias, if it has one.

        Parameters
        ----------
        alias
            Alias name pointing to the desired Entity

        Returns
        -------
            The Entity corresponding to the passed alias.
        """
        entity_id: str = self.aliases.get(alias, '')
        if entity_id:
            entity: Entity = self.get_entity_by_id(entity_id)
        else:
            self.create_entity(alias)
            entity: Entity = self.get_entity_by_alias(alias)
        return entity

    def get_entity_by_id(self, entity_id: str) -> Entity:
        return self.entities[entity_id]
