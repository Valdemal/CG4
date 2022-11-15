from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QApplication,
    QVBoxLayout, )

from figures import Spruce
from graphics.transformation import Transformation
from graphics.types import Point3D
from graphics_qt.images import SpruceImage
from graphics_qt.projections import CentralProjection
from widgets.views import FigureImageView


class MainWidget(QWidget):
    ROTATION_INCREACE = 1
    SCALE_INCREACE = 0.05

    def __init__(self, title: str, min_width: int, min_height: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(title)
        self.setMinimumSize(min_width, min_height)

        self.__figure = Spruce(Point3D(0, 0, 0), self.width() / 3, self.width() / 6, 3)

        image = SpruceImage(self.__figure, CentralProjection('z', 400), Transformation(45, 45, 1))

        self.__image_view = FigureImageView(image, parent=self)

        self.__init_layout()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        is_wheel_up = event.angleDelta().y() > 0
        increace = self.SCALE_INCREACE if is_wheel_up else -self.SCALE_INCREACE
        self.__image_view.scale_on(increace)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        match event.key():
            case Qt.Key_Left:
                self.__image_view.rotate_y(MainWidget.ROTATION_INCREACE)
            case Qt.Key_Right:
                self.__image_view.rotate_y(-MainWidget.ROTATION_INCREACE)
            case Qt.Key_Up:
                self.__image_view.rotate_x(MainWidget.ROTATION_INCREACE)
            case Qt.Key_Down:
                self.__image_view.rotate_x(-MainWidget.ROTATION_INCREACE)

    def __init_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__image_view)
        layout.setStretch(0, 5)
        layout.setStretch(1, 95)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWidget('Лабораторная работа №5', 800, 800)

    window.show()
    app.exec_()
