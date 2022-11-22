"""
Модуль реализующий отрисовку фигур и объектов пакета graphics средствами Qt
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPainterPath, QColor

from figures import Spruce

from graphics.figures import AbstractFigure
from graphics.help_functions import cyclic_pare_iter
from graphics.polygons import BasePolygon
from graphics.transformation import Transformation
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

    for p1, p2 in cyclic_pare_iter(points):
        path.lineTo(p2)
        painter.drawLine(p1, p2)

    if brush is not None:
        painter.fillPath(path, brush)


class AbstractFigureImage(ABC):
    """
    Образ фигуры.
    Определяет интерфейс отображения фигуры.
    Классы-потомки должны реализовать логику отрисовки фигуры.
    """

    def __init__(self, projection: Projection, transformation: Transformation):
        self.__projection = projection
        self.__transformation = transformation

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

    @property
    def transformation(self) -> Transformation:
        return self.__transformation


class FigureFrameworkImage(AbstractFigureImage):
    """
    Образ, выполняющий отрисовку каркаса фигуры.
    """

    def __init__(self,
                 figure: AbstractFigure,
                 projection: Projection,
                 transformation: Transformation,
                 pen: Optional[QPen] = None):
        super().__init__(projection, transformation)

        self.__figure = figure
        self.__pen = pen

    @property
    def figure(self) -> AbstractFigure:
        return self.__figure

    def draw(self, painter: QPainter):
        for polygon in self.__figure.polygons:
            connect_points([self.projection(point) for point in polygon], painter)


class Texture:
    def __init__(self, pen: QPen, brush: QBrush):
        self.__pen = pen
        self.__brush = brush

    def draw(self, polygon: BasePolygon, painter: QPainter, projection: Projection):
        painter.setPen(self.__pen)
        connect_points([
            projection(point) for point in polygon
        ], painter, self.__brush)


class PolygonImage:

    def __init__(self, polygon: BasePolygon, texture: Texture):
        self.__polygon_link = polygon
        self.__texture = texture
        self.__transformed_polygon: BasePolygon = None

    def transform(self, transformation: Transformation):
        self.__transformed_polygon = BasePolygon([
            transformation(point) for point in self.__polygon_link
        ])

    @property
    def polygon(self) -> BasePolygon:
        return self.__transformed_polygon

    def draw(self, painter: QPainter, projection: Projection):
        self.__texture.draw(self.polygon, painter, projection)


class SpruceImage(AbstractFigureImage):
    CONE_TEXTURE = Texture(QPen(Qt.black, 3), QBrush(QColor(0, 172, 0, 230)))
    LEG_TEXTURE = Texture(QPen(Qt.red, 3), QBrush(QColor(101, 48, 12, 210)))

    def __init__(self, spruce: Spruce, projection: Projection, transformation: Transformation):
        super().__init__(projection, transformation)
        self.__spruce = spruce

        self.__polygons_images = [
                                     PolygonImage(polygon, self.CONE_TEXTURE)
                                     for polygon in self.__spruce.cone
                                 ] + [
                                     PolygonImage(polygon, self.LEG_TEXTURE)
                                     for polygon in self.__spruce.leg
                                 ]

    @property
    def figure(self) -> AbstractFigure:
        return self.__spruce

    def draw(self, painter: QPainter):
        # Обновление положения образов многоугольников
        for polygon_image in self.__polygons_images:
            polygon_image.transform(self.transformation)

        # Сортировка образов по глубине
        self.__polygons_images.sort(key=lambda p: -p.polygon.center[self.projection.axle])

        # Отрисовка образов
        for polygon_image in self.__polygons_images:
            polygon_image.draw(painter, self.projection)
