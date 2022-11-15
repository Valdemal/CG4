"""
Модуль реализующий фигуры в трехмерном пространстве
"""

from abc import ABC, abstractmethod
from typing import List

from graphics.geometry_functions import avg
from graphics.types import Point3D, Matrix


class Polygon:
    def __init__(self, points: List[Point3D]):
        self.__points = points

    @property
    def points(self) -> List[Point3D]:
        return self.__points

    def apply_affine(self, affine_matrix: Matrix):
        for i in range(len(self.__points)):
            self.__points[i] = self.__points[i].apply_modification(affine_matrix)

    @property
    def center(self) -> Point3D:
        return avg(self.points)

    def copy(self) -> 'Polygon':
        return Polygon([point.copy() for point in self.points])


class AbstractFigure(ABC):
    @property
    @abstractmethod
    def polygons(self) -> List[Polygon]:
        pass

    @property
    @abstractmethod
    def center(self) -> Point3D:
        pass

    def apply_affine(self, affine_matrix: Matrix):
        for polygon in self.polygons:
            polygon.apply_affine(affine_matrix)


class BaseFigure(AbstractFigure):

    def __init__(self, polygons: List[Polygon], center: Point3D):
        self.__polygons = polygons
        self.__center = center

    @property
    def polygons(self) -> List[Polygon]:
        return self.__polygons

    @polygons.setter
    def polygons(self, value: List[Polygon]):
        self.__polygons = value

    @property
    def center(self) -> Point3D:
        return self.__center
