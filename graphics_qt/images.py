"""
Модуль реализующий отрисовку фигур и объектов пакета graphics средствами Qt
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPainterPath

from figures import Spruce
from graphics.figure import AbstractFigure, Polygon
from graphics.types import Axle
from graphics_qt.projections import Projection


def connect_points(points: List[QPointF],
                   painter: QPainter,
                   brush: Optional[QBrush] = None) -> None:
    """
    Соединяет точки на плоскости.
    :param points: Массив точек на плоскости
    :param painter: Отрисовщик Qt
    :param brush: Кисть для заливки нарисованного многоугольника
    """

    path = QPainterPath()
    path.moveTo(points[0])

    for i in range(1, len(points)):
        path.lineTo(points[i])
        painter.drawLine(points[i - 1], points[i])

    painter.drawLine(points[len(points) - 1], points[0])
    path.lineTo(points[0])

    if brush is not None:
        painter.fillPath(path, brush)


class AbstractFigureImage(ABC):
    """
    Образ фигуры.
    Определяет интерфейс отображения фигуры.
    Классы-потомки должны реализовать логику отрисовки фигуры.
    """

    def __init__(self, projection: Projection):
        self.__projection = projection

    @abstractmethod
    def draw(self, painter: QPainter):
        pass

    @property
    @abstractmethod
    def figure(self) -> AbstractFigure:
        pass

    @property
    def projection(self) -> Projection:
        return self.__projection

    @staticmethod
    def _draw_polygons(painter: QPainter, polygons: List[Polygon],
                       projection: Projection, brush: Optional[QBrush] = None):

        for polygon in polygons:
            connect_points([
                projection(point) for point in polygon.points
            ], painter, brush)


class FigureFrameworkImage(AbstractFigureImage):
    """
    Образ, выполняющий отрисовку каркаса фигуры.
    """

    def __init__(self,
                 figure: AbstractFigure,
                 projection: Projection,
                 pen: Optional[QPen] = None):

        super().__init__(projection)

        self.__figure = figure
        self.__pen = pen

    @property
    def figure(self) -> AbstractFigure:
        return self.__figure

    def draw(self, painter: QPainter):
        for polygon in self.__figure.polygons:
            connect_points([
                self.projection(point)
                for point in polygon.points
            ], painter)


class SpruceImage(AbstractFigureImage):
    CONE_BRUSH = QBrush(Qt.green)
    CONE_PEN = QPen(Qt.black, 3)

    LEG_BRUSH = QBrush(Qt.gray)
    LEG_PEN = QPen(Qt.red, 3)

    def __init__(self, spruce: Spruce, projection: Projection):
        super().__init__(projection)
        self.__spruce = spruce

    @property
    def figure(self) -> AbstractFigure:
        return self.__spruce

    def draw(self, painter: QPainter):
        def sort_polygons_by_deep(polygons: List[Polygon], axle: Axle) -> List[Polygon]:
            """
            a
            """
            result = sorted(polygons, key=lambda polygon: -polygon.center[axle])

            return result

        # Отрисовка конуса
        painter.setPen(self.CONE_PEN)
        self._draw_polygons(
            painter, sort_polygons_by_deep(self.__spruce.cone.polygons, self.projection.axle),
            self.projection, self.CONE_BRUSH
        )

        # Отрисовка ножки
        painter.setPen(self.LEG_PEN)
        self._draw_polygons(
            painter,
            sort_polygons_by_deep(self.__spruce.leg.polygons, self.projection.axle),
            self.projection, self.LEG_BRUSH
        )
