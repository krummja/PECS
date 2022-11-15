from __future__ import annotations
from beartype.typing import Any
from beartype.vale import Is
from typing import Annotated, TypeAlias


HasComponentID = Is[lambda cls: hasattr(cls, '__component_id__')]
Component_ = Annotated[type, HasComponentID]
IdStr = Annotated[str, Is[lambda id_str: id_str == id_str.upper()]]

Bases: TypeAlias = tuple[type, ...]
Namespace: TypeAlias = dict[str, Any]
