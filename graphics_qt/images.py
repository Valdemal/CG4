"""
Модуль реализующий отрисовку фигур и объектов пакета graphics средствами Qt
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainter, QPen, QBrush, QPainterPath

from graphics.figure import AbstractFigure
from graphics_qt.projections import Projection


def connect_points(points: List[QPointF], painter: QPainter) -> None:
    """
    Соединяет точки на плоскости.
    :param points: Массив точек на плоскости
    :param painter: Отрисовщик Qt
    """

    path = QPainterPath()
    path.moveTo(points[0])

    for i in range(1, len(points)):
        path.lineTo(points[i])
        painter.drawLine(points[i - 1], points[i])

    painter.drawLine(points[len(points) - 1], points[0])
    path.lineTo(points[0])


class AbstractFigureImage(ABC):
    """
    Образ фигуры.
    Определяет интерфейс отображения фигуры.
    Классы-потомки должны реализовать логику отрисовки фигуры.
    """

    @abstractmethod
    def draw(self, painter: QPainter):
        pass

    @property
    @abstractmethod
    def figure(self) -> AbstractFigure:
        pass

    @property
    @abstractmethod
    def projection(self) -> Projection:
        pass


class FigureFrameworkImage(AbstractFigureImage):
    """
    Образ, выполняющий отрисовку каркаса фигуры.
    """

    def __init__(self, figure: AbstractFigure, projection: Projection,
                 pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        self.__figure = figure
        self.__pen = pen
        self.__brush = brush
        self.__projection = projection

    @property
    def figure(self) -> AbstractFigure:
        return self.__figure

    @property
    def projection(self) -> Projection:
        return self.__projection

    def draw(self, painter: QPainter):
        for polygon in self.__figure.polygons:
            connect_points([
                self.__projection(point, self.__figure.center)
                for point in polygon.points
            ], painter)
