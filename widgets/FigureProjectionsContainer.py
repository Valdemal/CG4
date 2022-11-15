import copy
from enum import Enum, auto
from typing import Dict

from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy

from graphics.figure import BaseFigure
from graphics_qt.projections import OrthographicProjection, CentralProjection, Projection
from graphics.transformation import Transformation
from widgets.views import FigureProjectionView


class ProjectionType(Enum):
    ORTHOGRAPHIC = auto()
    CENTRAL = auto()


class FigureProjectionsContainer(QWidget):
    C = 200

    def __init__(
            self,
            figure: BaseFigure,
            transformaion: Transformation = Transformation(0, 0, 1),
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.__projections: Dict[ProjectionType, Projection] = {
            ProjectionType.ORTHOGRAPHIC: OrthographicProjection('z', transformaion),
            ProjectionType.CENTRAL: CentralProjection('z', self.C, copy.deepcopy(transformaion))
        }

        self.__current_projection_type = ProjectionType.CENTRAL

        self.__views = [
            FigureProjectionView(figure, OrthographicProjection('z')),
            FigureProjectionView(figure, OrthographicProjection('x')),
            FigureProjectionView(figure, OrthographicProjection('y')),
            FigureProjectionView(figure, self.__projections[self.__current_projection_type],
                                 transformaion, show_axis=(False, False), ),
        ]

        self.main_view.repaint()

        self.__init_layout()

    @property
    def current_projection_type(self) -> ProjectionType:
        return self.__current_projection_type

    @current_projection_type.setter
    def current_projection_type(self, value: ProjectionType):
        self.main_view.projection = self.__projections[value]
        self.__current_projection_type = value

    @property
    def main_view(self) -> FigureProjectionView:
        return self.__views[-1]

    def __init_layout(self):
        grid = QGridLayout()

        for i in range(len(self.__views)):
            self.__views[i].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            grid.addWidget(self.__views[i], i // 2, i % 2)

        self.setLayout(grid)
