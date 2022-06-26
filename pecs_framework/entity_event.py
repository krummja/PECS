from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    pass

from types import SimpleNamespace


class EventData(SimpleNamespace):
    _record: List[str] = []

    def __init__(self, /, **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self._record = [k for k in kwargs.keys()]

    def __setattr__(self, key: str, value: Any) -> None:
        if key not in self._record:
            self._record.append(key)
        super().__dict__.update({key: value})

    @property
    def record(self) -> Dict[str, Any]:
        namespace = super().__dict__
        return {k: namespace[k] for k in self._record}


class EntityEvent:

    def __init__(self, name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        if payload is not None:
            self._evt_data = EventData(**payload)
        else:
            self._evt_data = EventData(**{})

        self._handled: bool = False
        self._prevented: bool = False

    @property
    def data(self) -> EventData:
        return self._evt_data

    @property
    def handled(self) -> bool:
        return self._handled

    @property
    def prevented(self) -> bool:
        return self._prevented

    def handle(self) -> None:
        self._handled = True
        self._prevented = True

    def prevent(self) -> None:
        self._prevented = True

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EntityEvent):
            return self.name == other.name
        return False
