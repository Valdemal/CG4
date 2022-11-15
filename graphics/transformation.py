from graphics import affine
from graphics.types import Matrix, Point3D
from .geometry_functions import increase_angle


class Transformation:
    def __init__(self,
                 x_rotation: float,
                 y_rotation: float,
                 scale: float):
        # Инициализация свойсв преобразования
        self.x_rotation = x_rotation
        self.y_rotation = y_rotation
        self.scale = scale

    def to_affine_matrix(self) -> Matrix:
        return \
            affine.rotate(self.x_rotation, 'x') * \
            affine.rotate(self.y_rotation, 'y') * \
            affine.scaling(ky=self.scale, kx=self.scale, kz=self.scale)

    def increase_x_rotation(self, rotation_in_degrees: float) -> None:
        self.x_rotation = increase_angle(self.x_rotation, rotation_in_degrees)

    def increase_y_rotation(self, rotation_in_degrees: float) -> None:
        self.y_rotation = increase_angle(self.y_rotation, rotation_in_degrees)

    def __call__(self, point: Point3D) -> Point3D:
        return point.apply_modification(self.to_affine_matrix())

    @property
    def scale(self) -> float:
        return self.__scale

    @scale.setter
    def scale(self, value: float):
        self.__scale = value

    @property
    def x_rotation(self) -> float:
        return self.__x_rotation

    @x_rotation.setter
    def x_rotation(self, value: float):
        self.__x_rotation = value

    @property
    def y_rotation(self) -> float:
        return self.__y_rotation

    @y_rotation.setter
    def y_rotation(self, value: float):
        self.__y_rotation = value
