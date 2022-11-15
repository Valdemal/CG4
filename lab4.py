from typing import List, Callable

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QApplication,
    QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox,
)

from figures import Spruce
from graphics import affine
from graphics.types import Point3D
from graphics.transformation import Transformation
from widgets.FigureProjectionsContainer import FigureProjectionsContainer, ProjectionType


class SelectBox(QComboBox):
    """
    Костыль, созданный для того, чтобы события нажатия кнопки
    доходили до главного виджета, а не перехватывалиьс QComboBox
    """

    def __init__(self, items: List[str], current_item: str,
                 on_change: Callable,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.addItems(items)
        self.setCurrentText(current_item)
        self.currentIndexChanged.connect(on_change)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        e.ignore()


class ProjectionSelector(QWidget):
    PROJECTIONS_MAP = {
        'Центральная': ProjectionType.CENTRAL,
        'Ортографическая': ProjectionType.ORTHOGRAPHIC
    }

    def __init__(self, label: str,
                 projection_container: FigureProjectionsContainer,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__projection_container = projection_container

        self.__select_box = SelectBox(
            parent=self, items=self.PROJECTIONS_MAP.keys(),
            current_item=self.__get_current_projection_type(),
            on_change=self.__choose_projection
        )

        self.__label = QLabel(text=label, parent=self)
        self.__init_layout()

    def __get_current_projection_type(self):
        for key, value in self.PROJECTIONS_MAP.items():
            if value == self.__projection_container.current_projection_type:
                return key

    def __choose_projection(self) -> None:
        text = self.__select_box.currentText()

        if text in self.PROJECTIONS_MAP:
            self.__projection_container.current_projection_type = self.PROJECTIONS_MAP[text]
        else:
            raise ValueError(f"Неизвестный вид проекции {text}!")

    def __init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(self.__label)
        layout.addWidget(self.__select_box)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)


class MainWidget(QWidget):
    ROTATION_INCREACE = 1
    SCALE_INCREACE = 0.05

    def __init__(self, title: str, min_width: int, min_height: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(title)
        self.setMinimumSize(min_width, min_height)

        self.projections_container = FigureProjectionsContainer(
            figure=Spruce(Point3D(0, 0, 0), 150, 75, 3),
            transformaion=Transformation(45, 45, 1),
            parent=self
        )

        self.selector = ProjectionSelector(
            label='Тип проекции',
            projection_container=self.projections_container,
            parent=self
        )

        self.__init_layout()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        is_wheel_up = event.angleDelta().y() > 0
        increace = self.SCALE_INCREACE if is_wheel_up else -self.SCALE_INCREACE
        self.projections_container.main_view.scale_on(increace)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        match event.key():
            case Qt.Key_Left:
                self.projections_container.main_view.rotate_y(MainWidget.ROTATION_INCREACE)
            case Qt.Key_Right:
                self.projections_container.main_view.rotate_y(-MainWidget.ROTATION_INCREACE)
            case Qt.Key_Up:
                self.projections_container.main_view.rotate_x(MainWidget.ROTATION_INCREACE)
            case Qt.Key_Down:
                self.projections_container.main_view.rotate_x(-MainWidget.ROTATION_INCREACE)

    def __init_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.selector)
        layout.addWidget(self.projections_container)
        layout.setStretch(0, 5)
        layout.setStretch(1, 95)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWidget('Лабораторная работа №4', 800, 800)

    window.show()
    app.exec_()
