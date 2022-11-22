from abc import ABC, abstractmethod
from math import pi, cos, sin
from typing import List

from graphics.help_functions import avg, cyclic_pare_iter
from graphics.types import Point3D, Matrix


class AbstractPolygon(ABC):

    @property
    @abstractmethod
    def points(self) -> List[Point3D]:
        pass

    @abstractmethod
    def copy(self) -> 'AbstractPolygon':
        pass

    def apply_affine(self, affine_matrix: Matrix):
        for i in range(len(self.points)):
            self.points[i] = self.points[i].apply_modification(affine_matrix)

    @property
    def center(self) -> Point3D:
        return avg(self.points)

    def __iter__(self):
        return iter(self.points)


class BasePolygon(AbstractPolygon):
    def __init__(self, points: List[Point3D]):
        self.__points = points

    @property
    def points(self) -> List[Point3D]:
        return self.__points

    def copy(self) -> 'BasePolygon':
        return BasePolygon([point.copy() for point in self])


class Triangle(AbstractPolygon):

    def __init__(self, a: Point3D, b: Point3D, c: Point3D):
        self.__a = a
        self.__b = b
        self.__c = c

    @property
    def points(self) -> List[Point3D]:
        return [self.__a, self.__b, self.__c]

    def split(self) -> List['Triangle']:
        center = self.center

        return [Triangle(a, b, center) for a, b in cyclic_pare_iter(self.points)]

    def copy(self) -> 'Triangle':
        return Triangle(self.__a.copy(), self.__b.copy(), self.__c.copy())


class Rectangle(AbstractPolygon):

    def __init__(self,
                 top_left: Point3D, top_right: Point3D,
                 bottom_left: Point3D, bottom_right: Point3D, with_check=True):

        if with_check:
            if not self._is_rectangle(top_left, top_right, bottom_left, bottom_right):
                raise ValueError("Точки не образуют прямоугольник!")

        self.__top_left = top_left
        self.__top_right = top_right
        self.__bottom_left = bottom_left
        self.__bottom_right = bottom_right

    def copy(self) -> 'Rectangle':
        return Rectangle(self.__top_left, self.__top_right, self.__bottom_left, self.__bottom_right, False)

    @property
    def points(self) -> List[Point3D]:
        return [self.__top_left, self.__bottom_left, self.__bottom_right, self.__top_right]

    def split(self, sub_rects_count: int) -> List['Rectangle']:
        step = (self.__top_right - self.__top_left) / sub_rects_count

        prev_top = self.__top_left
        prev_bottom = self.__bottom_left
        res = []

        for i in range(sub_rects_count):
            cur_top = prev_top + step
            cur_bottom = prev_bottom + step

            res.append(Rectangle(prev_top, cur_top, prev_bottom, cur_bottom))

            prev_top = cur_top
            prev_bottom = cur_bottom

        return res

    @staticmethod
    def _is_rectangle(tl: Point3D, tr: Point3D, bl: Point3D, br: Point3D) -> bool:
        if tl.distance_between(tr) != bl.distance_between(br):
            return False

        if tl.distance_between(bl) != tr.distance_between(br):
            return False

        if tl.distance_between(br) != tr.distance_between(bl):
            return False

        return True


class RegularPolygon(BasePolygon):
    def __init__(self, center: Point3D, radius: float, sides_count: int):
        val = 2 * pi / sides_count

        super().__init__([
            Point3D(
                center.x + radius * cos(val * i),
                center.y,
                center.z + radius * sin(val * i),
            ) for i in range(sides_count)
        ])
