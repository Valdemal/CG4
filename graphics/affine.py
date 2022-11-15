"""
Модуль содержащий функции аффинных преобразований в пространстве.
"""

from math import sin, radians, cos
from typing import Literal, List

from graphics.types import Matrix, Axle


def transfer(delta_x: float = 1, delta_y: float = 1, delta_z: float = 1) -> Matrix:
    """
    Возвращает матрицу переноса.

    :param delta_x: перенос относительно оси Х
    :param delta_y: перенос относительно оси Y
    :param delta_z: перенос относительно оси Z
    """

    return Matrix([
        [1, 0, 0, delta_x],
        [0, 1, 0, delta_y],
        [0, 0, 1, delta_z],
        [0, 0, 0, 1]
    ])


def scaling(kx: float = 1, ky: float = 1, kz: float = 1) -> Matrix:
    """
    Возвращает матрицу масштабирования.

    :param kx: коэффициент масштабирования отнсительно оси Х
    :param ky: коэффициент масштабирования отнсительно оси Y
    :param kz: коэффициент масштабирования отнсительно оси Z
    """

    return Matrix([
        [kx, 0, 0, 0],
        [0, ky, 0, 0],
        [0, 0, kz, 0],
        [0, 0, 0, 1]
    ])


def reflection(axis: List[Axle]) -> Matrix:
    """
    Возвращает матрицу отражения.

    :param axis: список осей, хранящий оси отражения в любом порядке.
    например ['x'], ['y', 'x'], ['x','y','z']
    """

    def get_reflect_value(a: str):
        return -1 if axis.find(a) != -1 else 1

    return Matrix([
        [get_reflect_value('x'), 0, 0, 0],
        [0, get_reflect_value('y'), 0, 0],
        [0, 0, get_reflect_value('z'), 0],
        [0, 0, 0, 1]
    ])


def rotate(angle_in_degrees: float, axle: Axle) -> Matrix:
    """
    Возвращает матрицу поворота

    :param angle_in_degrees: угол поворота
    :param axle: ось поворота
    """

    def extend_matrix(arr: List[List[float]], i: int):
        arr.insert(i, [0, 0])

        for row in arr:
            row.insert(i, 0)

        arr[i][i] = 1

    angle_in_radians = radians(angle_in_degrees)
    cos_value = cos(angle_in_radians)
    sin_value = sin(angle_in_radians)

    a = [
        [cos_value, -sin_value],
        [sin_value, cos_value]
    ]

    help_i = 'xyz'.index(axle)

    extend_matrix(a, help_i)

    for row in a:
        row.append(0)

    a.append([0, 0, 0, 1])

    return Matrix(a)
