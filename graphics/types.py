"""
Модуль, в котором реализованы базовые типы пакета graphics
"""

from dataclasses import dataclass
from math import sqrt
from typing import List, Literal

Axle = Literal['x', 'y', 'z']

@dataclass
class Point3D:
    """Точка в трехмерном пространстве"""

    x: float
    y: float
    z: float

    def apply_modification(self, modification_matrix: 'Matrix') -> 'Point3D':
        return (modification_matrix * Vector(self)).to_point()

    def distance_between(self, other: 'Point3D') -> float:
        return sqrt(
            (other.x - self.x) ** 2 +
            (other.y - self.y) ** 2 +
            (other.z - self.z) ** 2
        )

    def coords(self) -> tuple:
        return self.x, self.y, self.z

    def copy(self) -> 'Point3D':
        return Point3D(self.x, self.y, self.z)

    def __getitem__(self, axle: Axle) -> float:
        match axle:
            case 'x':
                return self.x
            case 'y':
                return self.y
            case 'z':
                return self.z
            case _:
                raise IndexError(f'No ax named {axle}!')

    def __add__(self, other: 'Point3D'):
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Point3D'):
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __truediv__(self, num: float):
        return Point3D(self.x / num, self.y / num, self.z / num)

    def __neg__(self) -> 'Point3D':
        return Point3D(-self.x, -self.y, -self.z)

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"


class Matrix:
    """Матрица, необходимая для выполнения аффиных преобразований и проекции"""

    N = 4

    def __init__(self, array: List[List[float]] = None):

        if array is not None:
            self.__array = array
        else:
            self.__array = [[0 for _ in range(self.N)] for _ in range(self.N)]

    def __getitem__(self, item) -> List[float]:
        return self.__array[item]

    @staticmethod
    def identity():
        """Возвращает еденичную матрицу"""

        return Matrix([
            [0 if i != j else 1 for i in range(Matrix.N)]
            for j in range(Matrix.N)
        ])

    def __str__(self):
        res = ''

        for i in range(self.N):
            res += ' '.join([str(el) for el in self.__array[i]]) + '\n'

        return res

    def __mul__(self, value: 'Matrix' or 'Vector') -> 'Matrix' or 'Vector':
        if isinstance(value, Matrix):
            return self.__mul_on_matrix(value)
        elif isinstance(value, Vector):
            return self.__mul_on_vector(value)
        else:
            raise TypeError(f"Умножение матрицы на {value.__class__} не определено!")

    def __mul_on_matrix(self, other: 'Matrix') -> 'Matrix':
        result = Matrix()

        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    result.__array[i][j] += self.__array[i][k] * other.__array[k][j]

        return result

    def __mul_on_vector(self, vector: 'Vector') -> 'Vector':
        col = []

        for i in range(self.N):
            s = 0
            for j in range(self.N):
                s += self.__array[i][j] * vector[j]

            col.append(s)

        return Vector(tuple(col))


class Vector(tuple):
    """Вектор-столбец"""

    def __new__(cls, value: tuple or Point3D) -> 'Vector':
        if isinstance(value, tuple):
            return tuple.__new__(cls, value)
        elif isinstance(value, Point3D):
            return tuple.__new__(cls, (value.x, value.y, value.z, 1))
        else:
            raise TypeError(f"Конструктор Vector не определен для типа {value.__class__}")

    def to_point(self) -> Point3D:
        """
        Возращает точку, к которой был приведен вектор.

        :return: Точка в трехмерном пространстве.
        """

        return Point3D(*[coord / self[-1] for coord in self[:-1]])
