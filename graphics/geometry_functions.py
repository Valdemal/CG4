import functools
from typing import List

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
