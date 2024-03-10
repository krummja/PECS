from __future__ import annotations
from beartype.typing import TypeVar
from beartype.typing import TypedDict
from beartype.typing import Any

from pecs_framework._types import Bases, Namespace
from pecs_framework.events import EntityEvent

import sys
import traceback


class ComponentMeta(type):
    """Base Component Metaclass"""
    comp_id: str
    cbit: int
    _entity_id: str

    def __new__(
        cls: type[ComponentMeta],
        clsname: str,
        bases: Bases,
        namespace: Namespace,
    ) -> ComponentMeta:
        clsobj = super().__new__(cls, clsname, bases, namespace)
        clsobj.comp_id = clsname.upper()
        clsobj.cbit = 0
        return clsobj


class Component(metaclass=ComponentMeta):
    """Root Component class that all components extend."""
    _entity_id: str

    @property
    def entity_id(self) -> str:
        return self._entity_id

    def handle_event(self, evt: EntityEvent):
        self.on_event(evt)

        try:
            handler = getattr(self, f"on_{evt.name}")
            return handler(evt)
        except AttributeError:
            return None
        except Exception:
            traceback.print_exc(file=sys.stderr)
            raise

    def on_event(self, evt: EntityEvent) -> EntityEvent | None:
        pass


# Type variable ranging over Component instances
CT = TypeVar("CT", bound=Component)
