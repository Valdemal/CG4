"""
Модуль реализующий фигуры в трехмерном пространстве
"""

from abc import ABC, abstractmethod
from typing import List

from graphics.polygons import AbstractPolygon
from graphics.types import Point3D, Matrix


class AbstractFigure(ABC):
    @property
    @abstractmethod
    def polygons(self) -> List[AbstractPolygon]:
        pass

    @property
    @abstractmethod
    def center(self) -> Point3D:
        pass

    def __iter__(self):
        return iter(self.polygons)

    def apply_affine(self, affine_matrix: Matrix):
        for polygon in self.polygons:
            polygon.apply_affine(affine_matrix)


class BaseFigure(AbstractFigure):

    def __init__(self, polygons: List[AbstractPolygon], center: Point3D):
        self.__polygons = polygons
        self.__center = center

    @property
    def polygons(self) -> List[AbstractPolygon]:
        return self.__polygons

    @polygons.setter
    def polygons(self, value: List[AbstractPolygon]):
        self.__polygons = value

    @property
    def center(self) -> Point3D:
        return self.__center
