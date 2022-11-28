from pecs_framework import Loader

from .attacker import Attacker
from .health import Health
from .isfrozen import IsFrozen
from .position import Position
from .renderable import Renderable
from .velocity import Velocity


__all__ = [
    "Attacker",
    "Health",
    "IsFrozen",
    "Position",
    "Renderable",
    "Velocity",
]


loader = Loader(__file__)
