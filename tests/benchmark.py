from __future__ import annotations

import time
from pecs_framework import Engine
from pecs_framework import Component

from dataclasses import dataclass
from rich.console import Console


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
