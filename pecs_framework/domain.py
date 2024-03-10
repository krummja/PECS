from __future__ import annotations
from beartype.typing import TYPE_CHECKING
from beartype.typing import Any
from beartype.typing import TypedDict

from uuid import uuid1
from collections import OrderedDict
import json

if TYPE_CHECKING:
    from pecs_framework.component import Component
    from pecs_framework.engine import Engine
    from pecs_framework.prefab import EntityTemplate
    from pecs_framework.query import ComponentQuery

from pathlib import Path
from pecs_framework.entity import Entity
from pecs_framework.query import Query
from rich.console import Console


console = Console()

class ComponentDict(TypedDict):
    comp_id: str
    cbit: int
    data: dict[str, Any]


class EntityDict(TypedDict):
    alias: str | None
    components: list[ComponentDict]


class EntityRegistry:

    def __init__(self, domain: Domain) -> None:
        self.domain = domain
        self.alias_to_eid = OrderedDict()
        self.eid_to_alias = OrderedDict()
        self._map: dict[str, Entity] = OrderedDict()

    def __getitem__(self, key: str) -> Entity:
        return self._map[key]

    def __setitem__(self, key: str, entity: Entity) -> None:
        self._map[key] = entity

    def __iter__(self):
        return iter(self._map.values())

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
            id_: str = self.alias_to_eid.get(entity_or_alias, '')
        else:
            id_: str = entity_or_alias.eid
        return id_

    def create(
        self,
        alias: str | None = None,
        *,
        entity_id: str | None = None,
    ) -> Entity:
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
        entity = Entity(
            self.domain,
            entity_id if entity_id else self.domain.create_uid(),
        )
        self._map[entity.eid] = entity

        if alias:
            if alias in self.alias_to_eid:
                raise KeyError(f"Entity already exists with alias {alias}")
            self.alias_to_eid[alias] = entity.eid
            self.eid_to_alias[entity.eid] = alias

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
        entity_id: str = self.alias_to_eid.get(alias, '')
        if entity_id:
            return self.get_by_id(entity_id)
        else:
            self.create(alias)
            return self.get_by_alias(alias)

    def get_by_id(self, entity_id: str) -> Entity:
        return self._map[entity_id]

    def get_alias_for_entity(self, entity_or_eid: Entity | str) -> str | None:
        if isinstance(entity_or_eid, str):
            return self.eid_to_alias.get(entity_or_eid, None)
        return self.eid_to_alias.get(entity_or_eid.eid, None)

    def remove_entity_by_id(self, entity_id: str) -> None:
        self._map[entity_id]._on_entity_destroyed()
        del self._map[entity_id]

    def remove_entity_by_alias(self, alias: str) -> None:
        entity_id = self.get_entity_id(alias)
        if alias in self.alias_to_eid:
            del self.alias_to_eid[alias]
        self.remove_entity_by_id(entity_id)


class Domain:

    @staticmethod
    def create_uid() -> str:
        return str(uuid1())

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.reset()

    def reset(self) -> None:
        self.entities = EntityRegistry(self)
        self.queries: list[Query] = []

    def destroy_entity(self, entity: Entity | str) -> None:
        if isinstance(entity, str):
            if entity in self.entities.keys():
                self.entities.remove_entity_by_id(entity)
            else:
                self.entities.remove_entity_by_alias(entity)
        else:
            # if entity.eid in self.entities.aliases.values():
            for k, v in self.entities.alias_to_eid.items():
                if v == entity.eid:
                    alias = k
                    self.entities.remove_entity_by_alias(alias)
                    return
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

    def save(self, directory: Path, filename: str) -> None:
        output: dict[str, EntityDict] = {}

        for entity in self.entities:
            output[entity.eid] = {
                "alias": self.entities.get_alias_for_entity(entity.eid),
                "components": [],
            }

            for component in entity.components.values():
                component_data = serialize_component(component)
                output[entity.eid]["components"].append(component_data)

        write_to_file(directory, filename, output)

    def load(self, directory: Path, filename: str) -> None:
        if loaded_data := load_from_file(directory, filename):
            for eid, entity_data in loaded_data.items():
                alias = entity_data["alias"]
                component_data = entity_data["components"]

                entity = self.entities.create(alias=alias, entity_id=eid)

                for component_datum in component_data:
                    self.engine.components.attach(
                        entity,
                        component_datum["comp_id"],
                        {k: v for k, v in component_datum["data"].items()},
                    )


def write_to_file(
    directory: Path,
    filename: str,
    data_dict: dict[str, EntityDict],
) -> None:
    if not filename.endswith(".json"):
        filename = filename + ".json"
    with open(Path(directory, filename), "+w") as file:
        file.write(json.dumps(data_dict, indent=4))


def load_from_file(directory: Path, filename: str) -> dict[str, EntityDict]:
    if not (filename.endswith(".json")):
        filename = filename + ".json"
    with open(Path(directory, filename), "+r") as file:
        return json.loads(file.read())


def serialize_component(component: Component) -> ComponentDict:
    """
    Serialization should provide all of the necessary information needed to
    rebuild what is set up in `setup_ecs` anew, with the state that the
    components were in when they were serialized.
    """
    comp_id = component.__class__.comp_id
    cbit = component.__class__.cbit
    instance_data = vars(component)

    del instance_data["_entity_id"]

    return {
        "comp_id": comp_id,
        "cbit": cbit,
        "data": instance_data,
    }
