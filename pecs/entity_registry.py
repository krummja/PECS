from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pecs.engine import Engine

from collections import OrderedDict
from pecs.helpers import *
from pecs.component import Component, ComponentMeta
from pecs.entity_event import EntityEvent, EventData
from pecs.entity import Entity


class EntityRegistry:

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        

