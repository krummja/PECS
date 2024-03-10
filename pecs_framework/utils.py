from __future__ import annotations
from beartype.typing import TYPE_CHECKING
from beartype.typing import Iterable
from beartype.typing import Iterator
from beartype.typing import Sequence

if TYPE_CHECKING:
    from pecs_framework.prefab import ComponentTemplate

from itertools import groupby, islice


def subtract_bit(num: int, bit: int) -> int:
    return num & ~(1 << bit)


def add_bit(num: int, bit: int) -> int:
    return num | (1 << bit)


def has_bit(num: int, bit: int) -> bool:
    return (num >> bit) % 2 != 0


def bit_intersection(n1: int, n2: int) -> int:
    return n1 & n2


def all_equal(arr: Iterable) -> bool:
    g = groupby(arr)
    return next(g, True) and not next(g, False)


def iter_index(
    arr: Sequence[ComponentTemplate],
    value: ComponentTemplate,
    start: int = 0,
) -> Iterator[int]:
    try:
        # Check if the iterable supports indexing.
        seq_index = arr.index
    except AttributeError:
        it = islice(arr, start, None)
        for i, element in enumerate(it, start):
            if element is value or element == value:
                yield i
    else:
        i = start - 1
        try:
            while True:
                yield (i := seq_index(value, i + 1))
        except ValueError:
            pass
