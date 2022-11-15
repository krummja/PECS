from __future__ import annotations
from beartype.typing import *
from dataclasses import dataclass, field
from collections import OrderedDict

if TYPE_CHECKING:
    from pecs_framework.component import Component


@dataclass
class Entity:
    eid: str = ''
    cbits: int = 0
    components: OrderedDict[str, Component] = field(default_factory=OrderedDict)
