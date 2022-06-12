from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.engine import Engine
    from pecs.entity import Entity
    from pecs.world import World

from pecs.prefab_entity import PrefabEntity
from pecs.prefab_component import PrefabComponent


class PrefabRegistry:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._prefabs: Dict[str, PrefabEntity] = {}

    def register(self, data: Dict[str, Any] | str) -> None:
        """Serialize and store a PrefabEntity definition.

        Definitions come in the form of dicts, either directly from code or
        from deserialized JSON definition files.
        """
        prefab = self.unpack_definition(data)
        self._prefabs[prefab.name] = prefab

    def serialize(self, data: Dict[str, Any]) -> str:
        pass

    def deserialize(self, data: str) -> Dict[str, Any]:
        pass

    def unpack_definition(self, data: Dict[str, Any]) -> PrefabEntity:
        registered = self.get(data["name"])
        if registered:
            return registered

        prefab = PrefabEntity(data["name"])

        inherit: List[str] = []

        if isinstance(data.get("inherit"), list):
            inherit = data.get("inherit")
        elif isinstance(data.get("inherit"), str):
            inherit = [data.get("inherit")]

        prefab.inherit = [self.get(parent) for parent in inherit]
        components = data.get("components", [])

        for component_data in components:

            if isinstance(component_data, str):
                comp_id = component_data
                component_class = self.engine.components[comp_id]
                if component_class:
                    prefab.add_component(PrefabComponent(component_class))
                    continue

            if isinstance(component_data, dict):
                comp_id = component_data["type"]
                component_class = self.engine.components[comp_id]
                if component_class:
                    prefab.add_component(PrefabComponent(
                        component_class,
                        component_data.get("properties", {}),
                        component_data.get("overwrite", True)
                    ))
                    continue

            print(f"Unrecognized component reference {component_data} in prefab {data['name']}")

        return prefab

    def create(
            self, 
            world: World,
            name: str,
            properties: Optional[Dict[str, Any]] = None,
            uid: Optional[str] = None
        ) -> Entity | None:
        properties = properties or {}

        prefab = self.get(name)
        if not prefab:
            print(f"Could not instantiate {name} since it is not registered")
            return None

        entity = world.create_entity(uid if uid else None)
        entity._qeligible = False
        prefab.apply_to_entity(entity, properties)
        entity._qeligible = True
        return entity


    def clear(self) -> None:
        self._prefabs.clear()

    def get(self, name: str) -> PrefabEntity:
        return self._prefabs.get(name)
