from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.entity import Entity
    from pecs.entity_event import EntityEvent

import json
import sys
import traceback
from dataclasses import dataclass


IGNORED_ATTRIBUTES = [
    'allow_multiple',
    'cbit',
    'comp_id',
    'entity',
    'serialized',
]


class ComponentMeta(type):
    _comp_id: str
    _allow_multiple: bool
    _cbit: int
    _entity: Entity

    def __new__(
            mcs: Type[ComponentMeta],
            clsname: str,
            bases: Tuple[type, ...],
            namespace: Any
        ) -> ComponentMeta:
        clsobj = super().__new__(mcs, clsname, bases, namespace)
        clsobj._comp_id = str(clsname).upper()
        clsobj._allow_multiple = False
        clsobj._cbit = 0
        return clsobj

    @property
    def comp_id(self) -> str:
        return self._comp_id

    def __hash__(self) -> int:
        return hash(self._comp_id)


@dataclass
class Component(metaclass=ComponentMeta):
    _comp_id: str = ""
    _allow_multiple: bool = False
    _cbit: int = 0
    _entity: Entity | None = None
    _count: int = 0

    def __getstate__(self) -> str:
        state = {}
        for symbol in dir(self):
            if symbol[0] != "_" and symbol not in IGNORED_ATTRIBUTES:
                attr = getattr(self, symbol)
                if not isinstance(attr, Callable):
                    state[symbol] = attr
        return json.dumps(state)

    def __setstate__(self, serialized_state: str) -> None:
        state = json.loads(serialized_state)
        self.__dict__.update(state)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Component):
            return False
        return self._cbit == other._cbit

    def __str__(self) -> str:
        return str(self._comp_id) + ": " + str(self.__getstate__())

    def __hash__(self) -> int:
        return hash(self._comp_id)

    @property
    def allow_multiple(self) -> bool:
        return self._allow_multiple

    @property
    def cbit(self) -> int:
        return self._cbit

    @cbit.setter
    def cbit(self, value: int) -> None:
        self._cbit = value

    @property
    def comp_id(self) -> str:
        return self._comp_id

    @property
    def entity(self) -> Entity | None:
        if self._entity is not None:
            return self._entity

    @entity.setter
    def entity(self, value: Entity) -> None:
        self._entity = value

    @property
    def serialized(self) -> str:
        return json.dumps({self.comp_id: self.__getstate__()})

    def on_attached(self, entity: Entity) -> None:
        """Callback invoked whenever the component is attached to an entity."""
        pass

    def on_destroyed(self) -> None:
        """Callback invoked whenever the component is destroyed."""
        pass

    def on_event(self, evt: EntityEvent) -> Optional[EntityEvent]:
        """Generic event callback.

        This calls immediately prior to any custom callbacks on the Component.
        Define specific events in Component subclasses by adding methods
        prefixed with `on_`.
        """
        pass

    def _on_attached(self, entity: Entity) -> None:
        self._entity = entity
        self.on_attached(entity)

    def _on_destroyed(self) -> None:
        self.on_destroyed()
        self._entity = None

    def _on_event(self, evt: EntityEvent) -> Any:
        self.on_event(evt)
        try:
            handler = getattr(self, f"on_{evt.name}")
            return handler(evt)
        except AttributeError:
            return None
        except Exception:
            traceback.print_exc(file=sys.stderr)
            raise
