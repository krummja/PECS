from __future__ import annotations
from typing import *

from deepmerge import always_merger
from pecs_framework.component import ComponentMeta
from pecs_framework.entity import Entity


class PrefabComponent:

    def __init__(
            self,
            klass: ComponentMeta,
            properties: Optional[Dict[str, Any]] = None,
            overwrite: bool = True
        ) -> None:
        self.klass = klass
        self.properties = properties or {}
        self.overwrite = overwrite

    def apply_to_entity(
            self,
            entity: Entity,
            initial_props: Optional[Dict[str, Any]] = None
        ) -> None:
        initial_props = initial_props or {}

        if not self.klass.allow_multiple and entity.has(self.klass):
            if not self.overwrite:
                return
            component = entity[self.klass]
            entity.remove(component)

        props = always_merger.merge(self.properties, initial_props)
        entity.add(self.klass, props)
