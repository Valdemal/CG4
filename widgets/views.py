from abc import abstractmethod
from typing import Tuple, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtWidgets import QWidget

from graphics.figure import AbstractFigure
from graphics.types import Point3D
from graphics_qt.images import connect_points
from graphics_qt.images import AbstractFigureImage

from graphics_qt.projections import Projection
from graphics.transformation import Transformation


class AbstractViewWidget(QWidget):

    @property
    @abstractmethod
    def _transformation(self) -> Transformation:
        pass

    def scale_on(self, scale_increase: float):
        if self._transformation.scale + scale_increase > 0:
            self._transformation.scale += scale_increase
            self.repaint()

    def rotate_x(self, rotation_in_degrees: float):
        self._transformation.increase_x_rotation(rotation_in_degrees)
        self.repaint()

    def rotate_y(self, rotation_in_degrees: float):
        self._transformation.increase_y_rotation(rotation_in_degrees)
        self.repaint()

    @abstractmethod
    def paintEvent(self, event) -> None:
        pass


class FigureProjectionView(AbstractViewWidget):
    """Виджет отрисовывающий проекцию фигуры"""

    BORDER_PEN = QPen()
    AXIS_PEN = QPen(Qt.cyan, 2, Qt.DashDotLine)
    FIGURE_PEN = QPen(Qt.black, 2, Qt.SolidLine)

    def __init__(self,
                 figure: AbstractFigure,
                 projection: Projection,
                 transformation: Optional[Transformation] = None,
                 show_axis: Optional[Tuple[bool, bool]] = (True, True),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__figure = figure
        self.__projection = projection
        self.__transformation = transformation
        self.__painter = QPainter()
        self.__show_axis = show_axis

    @property
    def projection(self) -> Projection:
        return self.__projection

    @projection.setter
    def projection(self, value: Projection):
        self.__projection = value
        self.repaint()

    def paintEvent(self, event) -> None:
        self.__painter.begin(self)
        self.__painter.setRenderHint(QPainter.Antialiasing)

        self.__draw_working_space(event)

        self.__painter.translate(self.width() // 2, self.height() // 2)

        self.__painter.setPen(self.FIGURE_PEN)
        self.__draw_figure_with_projection()

        self.__painter.end()

    @property
    def _transformation(self) -> Transformation:
        return self.__transformation

    def __draw_figure_with_projection(self) -> None:
        """
        Отрисовывает трехмерную фигуру на плоскости с учетом проекции.
        """
        def proxy_point(point: Point3D):
            if self._transformation is None:
                return point
            else:
                return self._transformation(point)

        for polygon in self.__figure.polygons:

            connect_points([
                self.__projection(proxy_point(point))
                for point in polygon.points
            ], self.__painter)

    def __draw_working_space(self, event):
        """Выполняет отрисовку рабочей области(границ и осей)"""

        self.__painter.setPen(self.BORDER_PEN)
        self.__painter.drawRect(event.rect())

        self.__painter.setPen(self.AXIS_PEN)
        if self.__show_axis[0]:
            height_half = self.height() // 2

            self.__painter.drawLine(
                0, height_half,
                self.width(), height_half
            )

        if self.__show_axis[1]:
            width_half = self.width() // 2
            self.__painter.drawLine(
                width_half, 0,
                width_half, self.height()
            )


class FigureImageView(AbstractViewWidget):
    """Виджет отрисовывающий образ фигуры"""

    def __init__(self, image: AbstractFigureImage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__image = image
        self.__painter = QPainter()

    def paintEvent(self, event) -> None:
        self.__painter.begin(self)
        self.__painter.setRenderHint(QPainter.Antialiasing)
        self.__painter.translate(self.width() // 2, self.height() // 2)

        self.__image.draw(self.__painter)

        self.__painter.end()

    @property
    def _transformation(self) -> Transformation:
        return self.__image.transformation
