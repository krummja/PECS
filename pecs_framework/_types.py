from __future__ import annotations
from beartype.typing import Any
from beartype.vale import Is
from typing import Annotated, TypeAlias


HasComponentID = Is[lambda cls: hasattr(cls, 'comp_id')]
Component_ = Annotated[type, HasComponentID]
CompId = Annotated[str, Is[lambda id_str: id_str == id_str.upper()]]
Alias = Annotated[str, Is[lambda alias: alias[0:4] == 'ent_']]

Bases: TypeAlias = tuple[type, ...]
Namespace: TypeAlias = dict[str, Any]
