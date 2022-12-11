from __future__ import annotations
from beartype.typing import *

from uuid import uuid1
from collections import OrderedDict

if TYPE_CHECKING:
    from pecs_framework.engine import Engine
    from pecs_framework.query import ComponentQuery
    from pecs_framework.prefab import EntityTemplate

from pecs_framework.entities import Entity
from pecs_framework.query import Query
from rich.console import Console
from rich import inspect


console = Console()


class EntityRegistry:

    def __init__(self, domain: Domain) -> None:
        self.domain = domain
        self.aliases = OrderedDict()
        self._map: dict[str, Entity] = OrderedDict()

    def __getitem__(self, key: str) -> Entity:
        return self._map[key]

    def __setitem__(self, key: str, entity: Entity) -> None:
        self._map[key] = entity

    def keys(self):
        return self._map.keys()

    def values(self):
        return self._map.values()
    
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
    
    def create(self, alias: str | None = None) -> Entity:
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
        entity = Entity(self.domain, self.domain.create_uid())
        self._map[entity.eid] = entity
        
        if alias:
            if alias in self.aliases.keys():
                raise KeyError(f"Entity already exists with alias {alias}")
            self.aliases[alias] = entity.eid

        return entity

    def create_from_prefab(
        self,
        template: str,
        properties: dict[str, Any] | None = None,
        alias: str | None = None,
    ) -> Entity:
        entity = self.create(alias)
        prefabs = self.domain.engine.prefabs

        entity_template: EntityTemplate = prefabs.build_prefab(template)
        comp_props = prefabs.resolve_overrides(entity_template.components)

        # Gather up keys from our resolved overrides.
        keys = [key.upper() for key in comp_props.keys()]
        if properties:

            # Normalize key names from passed properties for matching.
            properties = {k.upper(): v for k, v in properties.items()}

            # Match against resolved comp_props and update with overrides.
            for name, prop_block in properties.items():
                if name in keys:
                    comp_props[name].update(prop_block)

        # Finally, attach concrete components to the entity, using the resolved
        # props from the process above.
        for name, props in comp_props.items():
            self.domain.engine.components.attach(entity, name, props)
        
        return entity

    def get_by_alias(self, alias: str) -> Entity:
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
            return self.get_by_id(entity_id)
        else:
            self.create(alias)
            return self.get_by_alias(alias)

    def get_by_id(self, entity_id: str) -> Entity:
        return self._map[entity_id]

    def remove_entity_by_id(self, entity_id: str) -> None:
        self._map[entity_id]._on_entity_destroyed()
        del self._map[entity_id]

    def remove_entity_by_alias(self, alias: str) -> None:
        entity_id = self.get_entity_id(alias)
        self.remove_entity_by_id(entity_id)


class Domain:
    
    @staticmethod
    def create_uid() -> str:
        return str(uuid1())
    
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.entities = EntityRegistry(self)
        self.queries: List[Query] = []

    def destroy_entity(self, entity: Entity | str) -> None:
        if isinstance(entity, str):
            if entity in self.entities.keys():
                self.entities.remove_entity_by_id(entity)
            else:
                self.entities.remove_entity_by_alias(entity)
        else:
            self.entities.remove_entity_by_id(entity.eid)

    def create_query(
        self,
        all_of: ComponentQuery | None = None,
        any_of: ComponentQuery | None = None,
        none_of: ComponentQuery | None = None,
    ) -> Query:        
        query = Query(self, all_of, any_of, none_of)
        self.queries.append(query)
        return query

    def candidate(self, entity: Entity) -> None:
        for query in self.queries:
            query.candidate(entity)
