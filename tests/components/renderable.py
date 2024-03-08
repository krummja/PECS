from __future__ import annotations
from typing import TypeAlias
from dataclasses import dataclass
from pecs_framework.component import Component


Color: TypeAlias = tuple[int, int, int] | list[int]


@dataclass
class Renderable(Component):
    """Representation of an Entity's rendered appearance."""
    ch: str = '?'
    fg: Color = (255, 255, 255)
    bg: Color = (0, 0, 0)

    def __post_init__(self) -> None:
        if isinstance(self.fg, list):
            self.fg = (self.fg[0], self.fg[1], self.fg[2])
        if isinstance(self.bg, list):
            self.bg = (self.bg[0], self.bg[1], self.bg[2])
