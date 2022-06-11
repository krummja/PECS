from __future__ import annotations
from typing import *
from collections import deque


T = TypeVar("T")


def subtract_bit(num: int, bit: int) -> int:
    return num & ~(1 << bit)


def add_bit(num: int, bit: int) -> int:
    return num | (1 << bit)


def has_bit(num: int, bit: int) -> bool:
    return (num >> bit) % 2 != 0


def bit_intersection(n1: int, n2: int) -> int:
    return n1 & n2


def deque_filter(
        lst: list[T],
        condition: Callable[[T], bool],
        replace: Optional[Callable[[T], T]] = None
) -> MutableSequence[T]:
    """Utility function for filtering a deque.

    :param lst:
        List of items of type T to populate the deque.
    :param condition:
        Function that takes in items of type T and returns True if they meet
        the condition.
    :param replace:
        Optional function that replaces for the item that matches the condition
        prior to appending that item back into the deque.
    :return:
        The filtered deque.
    """
    lst = deque(lst)

    for _ in range(len(lst)):
        item = lst.popleft()

        if condition(item):
            if replace:
                item = replace(item)
            lst.append(item)

    return lst
