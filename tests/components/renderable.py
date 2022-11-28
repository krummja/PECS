from __future__ import annotations
from typing import TypeAlias
from dataclasses import dataclass
from pecs_framework.component import Component



Color: TypeAlias = tuple[int, int, int]

@dataclass
class Renderable(Component):
    """Representation of an Entity's rendered appearance."""
    ch: str
    fg: Color
    bg: Color
