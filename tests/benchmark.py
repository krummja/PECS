from __future__ import annotations
from beartype.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pecs_framework.prefab import EntityTemplate
    from pecs_framework.prefab import ComponentTemplate

import time

import cProfile

from pecs_framework import Engine
from pecs_framework.base_system import BaseSystem
from pecs_framework.base_system import Loop
from pecs_framework import Component
from pecs_framework.entities import utils

from dataclasses import dataclass, field

from rich.console import Console

from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput


@dataclass
class ComponentA(Component):
    """Simple component"""


@dataclass
class ComponentB(Component):
    k: int = 0


@dataclass
class ComponentC(Component):
    """Another simple component"""


def test(iterations: int = 30, entity_count: int = 10000) -> None:

    console = Console()
    total_time: float = 0.0

    for n in range(iterations):

        ecs = Engine()
        domain = ecs.create_domain("Benchmark")

        ecs.components.register(ComponentA)
        ecs.components.register(ComponentB)
        ecs.components.register(ComponentC)

        domain.create_query(all_of=[ComponentA])
        domain.create_query(all_of=[ComponentB])
        domain.create_query(all_of=[ComponentC])

        start = time.time() * 1000

        for i in range(entity_count):
            entity = domain.entities.create(f"e{i}")

            ecs.components.attach(entity, ComponentA)
            ecs.components.attach(entity, ComponentB)
            ecs.components.attach(entity, ComponentC)

            domain.destroy_entity(entity)

        end = time.time() * 1000
        delta = end - start

        console.print(f"T{n} {round(delta)}ms")
        total_time += delta

    avg = total_time / iterations

    console.print(f"AVG({iterations}) {round(avg)}ms")


if __name__ == '__main__':
    test(30, 10000)
