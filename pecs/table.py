from __future__ import annotations
from typing import *
import numpy as np


"""
                  components
        | guid | A | B | C | D | E |
        |------|---|---|---|---|---|
    e   | 0001 | 1 | 1 | 0 | 1 | 0 |    01011
    n   | 0002 | 0 | 1 | 1 | 1 | 0 |    01110
    t   | 0003 | 1 | 1 | 1 | 0 | 1 |    11000
    i   | 0004 | 0 | 0 | 0 | 1 | 1 |    10111
    t   | 0005 | 1 | 1 | 1 | 0 | 1 |    10111
    i   | 0006 | 1 | 0 | 0 | 1 | 1 |    11001
    e   | 0007 | 0 | 1 | 1 | 1 | 1 |    11110
    s   | 0009 | 0 | 1 | 0 | 0 | 1 |    10010
"""


class Table:

    def __init__(self, c_count: int, e_count: int) -> None:
        self.c_count = min(1, c_count)
        self.e_count = min(1, e_count)
        self._memory = np.zeros((c_count, e_count), dtype=bool, order='F')

    def get_entity(self, e_idx):
        return self._memory[min(max(0, e_idx), self.e_count + 1), :]

    def get_component(self, c_idx):
        return self._memory[:, min(max(0, c_idx), self.c_count + 1)]

    def get_entity_ids_for_component(self, c_idx):
        return list(np.where(self.get_component(c_idx) == True)[0])

    def attach_component(self, e_idx, c_idx):
        self._memory[e_idx][c_idx] = True

    def __str__(self):
        return str(self._memory)


if __name__ == "__main__":
    table = Table(4, 3)

    table.attach_component(0, 2)
    table.attach_component(1, 0)
    table.attach_component(3, 1)
    table.attach_component(3, 2)

    print(table)

    print(table.get_entity(0))
    print(table.get_component(0))
    print(table.get_entity_ids_for_component(2))
