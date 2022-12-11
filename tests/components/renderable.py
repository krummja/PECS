from __future__ import annotations
from typing import TypeAlias
from dataclasses import dataclass
from pecs_framework.component import Component


Color: TypeAlias = tuple[int, int, int]


@dataclass
class Renderable(Component):
    """Representation of an Entity's rendered appearance."""
    ch: str = '?'
    fg: Color = (255, 255, 255)
    bg: Color = (0, 0, 0)

    def __post_init__(self) -> None:
        if isinstance(self.fg, list):
            self.fg = tuple(self.fg)
        if isinstance(self.bg, list):
            self.bg = tuple(self.bg)
