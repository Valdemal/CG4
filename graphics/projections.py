"""
Модуль содержащий функции проектирования.
"""

from typing import Literal

from graphics.types import Matrix


def _get_orthographic_matrix(i: int) -> Matrix:
    matrix = Matrix.identity()
    matrix[i][i] = 0
    return matrix


def orthographic(axle: Literal['x', 'y', 'z']) -> Matrix:
    """
    :param axle: Плоскость проекции.
    :return: Матрица ортографической проекции.
    """
    i = 'xyz'.index(axle)

    return _get_orthographic_matrix(i)


def central(axle: Literal['x', 'y', 'z'], distance_from_screen: float) -> Matrix:
    i = 'xyz'.index(axle)

    matrix = _get_orthographic_matrix(i)
    matrix[-1][i] = 1 / distance_from_screen

    return matrix
