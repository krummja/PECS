from __future__ import annotations
from typing import *

from pecs.component import Component
from pecs.entity import Entity


class PrefabComponent:

    def __init__(
            self,
            klass: Component,
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
        pass
