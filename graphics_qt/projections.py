"""
Модуль реализующий проекцию трехмерных точек пакет graphics в двумерные точки QPointF
"""
from abc import ABC, abstractmethod
from typing import Literal, Optional

from PyQt5.QtCore import QPointF

from graphics import projections
from graphics.types import Point3D, Matrix
from graphics.transformation import Transformation


class Projection(ABC):
    """
    Абстрактный класс проекции. Реализует паттерн "Команда".
    В качестве состояния хранит матрицу проекции
    """

    def __init__(self,
                 projection_matrix: Matrix,
                 axle: Literal['x', 'y', 'z'],
                 transformation: Optional[Transformation] = None):
        self._projection_matrix = projection_matrix
        self.__transformation = transformation
        self._axle = axle

    @abstractmethod
    def __call__(self, point: Point3D, center: Point3D) -> QPointF:
        """
        Метод выполняющий проекцию трехмерной точки Point3D в двумерную QPointF
        :param point: точка в трехмерном пространстве
        :return: точка на плоскости
        """

        pass

    @property
    def transformation(self) -> Transformation:
        return self.__transformation


class OrthographicProjection(Projection):

    def __init__(self, axle: Literal['x', 'y', 'z'], transformation: Optional[Transformation] = None):
        super().__init__(projections.orthographic(axle), axle, transformation)

    def __call__(self, point: Point3D, center: Point3D) -> QPointF:

        matrix = self._projection_matrix
        if self.transformation is not None:
            matrix *= self.transformation.to_affine_matrix()

        transformed_point = point.apply_modification(matrix)

        match self._axle:
            case 'x':
                return QPointF(transformed_point.z, -transformed_point.y)
            case 'y':
                return QPointF(transformed_point.x, -transformed_point.z)
            case 'z':
                return QPointF(transformed_point.x, -transformed_point.y)

    @staticmethod
    def __new_point(point: Point3D, center: Point3D) -> Point3D:
        return Point3D(point.x - center.x, point.y - center.x, point.z)


class CentralProjection(OrthographicProjection):
    def __init__(self, ax: Literal['x', 'y', 'z'],
                 distance_from_screen: float,
                 transformation: Optional[Transformation] = None,
                 ):

        super().__init__(ax, transformation)
        self.set_distance(distance_from_screen)

    def set_distance(self, distance_from_screen):
        self._projection_matrix = projections.central(self._axle, distance_from_screen)
