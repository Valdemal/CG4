"""
Модуль реализующий отрисовку фигур и объектов пакета graphics средствами Qt
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPainterPath

from figures import Spruce
from graphics.figure import AbstractFigure, Polygon
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
            connect_points([
                self.projection(point)
                for point in polygon.points
            ], painter)


class Texture:
    def __init__(self, pen: QPen, brush: QBrush):
        self.__pen = pen
        self.__brush = brush

    def draw(self, polygon: Polygon, painter: QPainter, projection: Projection):
        painter.setPen(self.__pen)
        connect_points([
            projection(point) for point in polygon.points
        ], painter, self.__brush)


class PolygonImage:

    def __init__(self, polygon: Polygon, texture: Texture):
        self.__polygon_link = polygon
        self.__texture = texture
        self.__transformed_polygon: Polygon = None

    def transform(self, transformation: Transformation):
        self.__transformed_polygon = Polygon([
            transformation(point) for point in self.__polygon_link.points
        ])

    @property
    def polygon(self) -> Polygon:
        return self.__transformed_polygon

    def draw(self, painter: QPainter, projection: Projection):
        self.__texture.draw(self.polygon, painter, projection)


class SpruceImage(AbstractFigureImage):
    CONE_TEXTURE = Texture(QPen(Qt.black, 3), QBrush(Qt.green))
    LEG_TEXTURE = Texture(QPen(Qt.red, 3),  QBrush(Qt.gray))

    def __init__(self, spruce: Spruce, projection: Projection, transformation: Transformation):
        super().__init__(projection, transformation)
        self.__spruce = spruce

        self.__polygons_images = [
            PolygonImage(polygon, self.CONE_TEXTURE)
            for polygon in self.__spruce.cone.polygons
        ] + [
            PolygonImage(polygon, self.LEG_TEXTURE)
            for polygon in self.__spruce.leg.polygons
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
