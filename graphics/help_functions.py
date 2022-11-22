import functools
from typing import List, Iterable

from graphics.types import Point3D


def increase_angle(angle: float, increase_in_degrees: float) -> float:
    angle += increase_in_degrees

    if angle > 360:
        angle %= 360
    elif angle < -360:
        angle %= -360

    return angle


def avg(points: List[Point3D]) -> Point3D:

    return functools.reduce(lambda x, y: x + y, points) / len(points)


def cyclic_pare_iter(container: Iterable):
    it = iter(container)
    try:
        prev = first = next(it)
        current = next(it)

        while True:
            try:
                yield prev, current
                prev = current
                current = next(it)

            except StopIteration:
                yield current, first
                break

    except StopIteration:
        raise IndexError("Длина контейнера должна быть не менее 2!")


def cyclic_iter(container: Iterable):
    it = iter(container)
    try:
        current = first = next(it)

        while True:
            try:
                yield current
                current = next(it)
            except StopIteration:
                yield first
                break

    except StopIteration:
        raise IndexError("Длина контейнера должна быть не менее 1!")

