from __future__ import annotations
from beartype.typing import Any, TYPE_CHECKING, Deque

if TYPE_CHECKING:
    from pecs_framework.engine import Engine
    from pecs_framework._types import CompId
    from pecs_framework.component import Component

import os
import json
from copy import copy, deepcopy
from pathlib import Path
from dataclasses import dataclass, field
from pecs_framework.utils import iter_index
from collections import deque


@dataclass
class ComponentTemplate:
    component_type: str
    properties: dict[str, Any]

    @property
    def name(self) -> CompId:
        return self.component_type.upper()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ComponentTemplate):
            return self.name == other.name
        return False


@dataclass
class EntityTemplate:
    name: str
    inherit: list[str] = field(default_factory=list)
    components: list[ComponentTemplate] = field(default_factory=list)


class PrefabBuilder:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.domain = engine.domain
        self._templates: dict[str, EntityTemplate] = {}

        self._root: EntityTemplate | None = None
        self._temp: Deque[EntityTemplate] = deque([])
        self._depth = 0

    @property
    def templates(self) -> dict[str, EntityTemplate]:
        return self._templates

    def deserialize(self, definition: str) -> EntityTemplate:
        data: dict[str, Any] = dict(json.loads(definition))
        components: list[ComponentTemplate] = []

        if 'components' in data.keys():
            for comp_def in data['components']:
                component_template = ComponentTemplate(
                    component_type=comp_def['type'],
                    properties=comp_def.get('properties', {}),
                )

                components.append(component_template)

        entity_template = EntityTemplate(
            name=data['name'],
            inherit=data.get('inherit', []),
            components=components,
        )

        return entity_template

    def register(self, path: str, file: str) -> None:
        full_path = os.path.join(str(Path(path) / file))
        if full_path[-5:] != '.json':
            full_path += '.json'

        with open(full_path, 'r') as prefab_file:
            data = prefab_file.read()

        prefab = self.deserialize(data)
        self._templates[prefab.name] = prefab

    def build_prefab(self, template_name: str) -> EntityTemplate:
        copied_prefab = deepcopy(self._templates[template_name])

        # Traverse up the inheritance tree, writing all found entity templates
        # to the temp array to cache them.
        prefab = self.recurse_template(copied_prefab)

        # Once we've returned to this method, extend our original prefab's
        # components with the components of each found parent template.

        # prefab_components = deque(prefab.components)
        for template in self._temp:
            # for component in template.components:
            #     prefab_components.append(component)
            prefab.components.extend(template.components)

        # Clear the temp array so we don't pollute other templates.
        self._temp = deque([])
        return prefab

    def recurse_template(self, template: EntityTemplate) -> EntityTemplate:
        inherited = deque(template.inherit)
        while len(inherited) > 0:
            parent = inherited.popleft()
            self._temp.appendleft(self.recurse_template(self.templates[parent]))
        else:
            return template

        # for parent in template.inherit:
        #     self._temp.append(self.recurse_template(self.templates[parent]))
        # return template

    def resolve_overrides(
        self,
        components: list[ComponentTemplate]
    ) -> dict[str, dict[str, Any]]:
        """
        From a list of potentially non-unique ComponentTemplate objects, resolve
        all property blocks down to unary blocks, where blocks from descendant
        components override those of their ancestor components in the
        inheritance tree.

        Parameters
        ----------
        components
            A list of ComponentTemplate objects from the EntityTemplate's
            inheritance tree.

        Returns
        -------
            The resolved properties for all components in the EntityTemplate
            definition.
        """
        index_map = {}
        for component in components:
            component_indices = [_ for _ in iter_index(components, component)]
            index_map[component.name] = component_indices

        comp_props = {}
        for name, indices in index_map.items():
            active = None
            unresolved = deque([components[idx].properties for idx in indices])

            while len(unresolved) > 1:
                active = unresolved.popleft()
                unresolved[0].update(active)
            else:
                resolved = {name: unresolved[0]}

            comp_props.update(resolved)

        return comp_props
