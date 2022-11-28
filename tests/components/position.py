from __future__ import annotations

from dataclasses import dataclass
from pecs_framework.component import Component


@dataclass
class Position(Component):
    """Representation of an Entity's position in 2D space."""
    x: int
    y: int

    @property
    def xy(self) -> tuple[int, int]:
        return self.x, self.y
