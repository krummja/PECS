from __future__ import annotations

from dataclasses import dataclass
from pecs_framework.component import Component


@dataclass
class Noun(Component):
    text: str = '<unset>'
