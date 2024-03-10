from __future__ import annotations
from beartype.typing import TYPE_CHECKING, Any
from beartype.typing import TypedDict

if TYPE_CHECKING:
    from pecs_framework.engine import Engine
    from pecs_framework.prefab import EntityTemplate
    from pecs_framework.prefab import ComponentTemplate

from pathlib import Path
import pickle
import os
import pytest

from pecs_framework import Engine
from pecs_framework.base_system import BaseSystem
from pecs_framework.base_system import Loop

from pecs_framework.component import Component

from tests.components import Attacker
from tests.components import Health
from tests.components import IsFrozen
from tests.components import Noun
from tests.components import Position
from tests.components import Renderable
from tests.components import Velocity
from tests.components import loader

import json

from rich import inspect
from rich.console import Console


TEST_DIR = Path(__file__).parent.resolve()
PREFABS = str(Path(TEST_DIR, 'prefabs'))
DATA = str(Path(TEST_DIR, "data"))


class ComponentDict(TypedDict):
    comp_id: str
    cbit: int
    data: dict[str, Any]


class EntityDict(TypedDict):
    alias: str | None
    components: list[ComponentDict]


def setup_ecs() -> Engine:
    ecs = Engine(loader)
    domain = ecs.create_domain("World")
    ecs.components.load("tests.components")

    ecs.prefabs.register(PREFABS, 'game_object')
    ecs.prefabs.register(PREFABS, 'character')
    ecs.prefabs.register(PREFABS, 'player')
    ecs.prefabs.register(PREFABS, "combatant")
    ecs.prefabs.register(PREFABS, "human_attacker")

    domain.entities.create('e1')
    domain.entities.create('e2')
    domain.entities.create('e3')
    domain.entities.create('e4')
    domain.entities.create()

    for i, entity in enumerate(domain.entities.values()):
        ecs.components.attach(entity, "position", {'x': 10, 'y': 10})
        ecs.components.attach(entity, Velocity, {'x': 1, 'y': 1})
        ecs.components.attach(entity, Renderable('@', (255, 0, 255), (0, 0, 0)))
        ecs.components.attach(entity, Health(100))

        if i > 2:
            ecs.components.attach(entity, IsFrozen)

        ecs.components.attach(entity, Attacker(10))

    return ecs


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


def pickle_component(component: Component) -> bytes:
    return pickle.dumps(component)


def write_to_file(filename: str, data_dict: dict[str, EntityDict]) -> None:
    if not filename.endswith(".json"):
        filename = filename + ".json"
    with open(Path(DATA, filename), "+w") as file:
        file.write(json.dumps(data_dict, indent=4))


def load_from_file(filename: str) -> dict[str, EntityDict]:
    if not (filename.endswith(".json")):
        filename = filename + ".json"
    with open(Path(DATA, filename), "+r") as file:
        return json.loads(file.read())


def pickling() -> None:
    console = Console()
    ecs = setup_ecs()
    domain = ecs.domain

    pickled = []

    for entity in domain.entities:
        for _, component in entity.components.items():
            pickled.append(pickle_component(component))

    for component in pickled:
        loaded = pickle.loads(component)
        console.print(vars(loaded))


def saving() -> None:
    ecs = setup_ecs()
    domain = ecs.domain

    output: dict[str, EntityDict] = {}
    for entity in domain.entities:
        output[entity.eid] = {
            "alias": domain.entities.get_alias_for_entity(entity.eid),
            "components": [],
        }

        for _, component in entity.components.items():
            component_data = serialize_component(component)
            output[entity.eid]["components"].append(component_data)

    write_to_file("save.json", output)


def loading() -> None:
    console = Console()
    ecs = Engine(loader)
    domain = ecs.create_domain("World")
    ecs.components.load("tests.components")

    loaded = load_from_file("save.json")

    for eid, entity_data in loaded.items():
        alias = entity_data["alias"]
        component_data = entity_data["components"]

        entity = domain.entities.create(alias=alias, entity_id=eid)

        for component_datum in component_data:
            ecs.components.attach(
                entity,
                component_datum["comp_id"],
                {k: v for k, v in component_datum["data"].items()},
            )

    console.print(dict(domain.entities))


def main() -> None:
    saving()
    loading()


if __name__ == '__main__':
    main()
