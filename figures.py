from math import pi, cos, sin
from typing import List

from graphics.figure import BaseFigure, Polygon, AbstractFigure
from graphics.geometry_functions import avg
from graphics.types import Point3D


class RegularPolygon(Polygon):
    def __init__(self, center: Point3D, radius: float, sides_count: int):
        val = 2 * pi / sides_count

        super().__init__([
            Point3D(
                center.x + radius * cos(val * i),
                center.y,
                center.z + radius * sin(val * i),
            ) for i in range(sides_count)
        ])


class Cone(BaseFigure):
    SIDES_COUNT = 10

    def __init__(self, base_center: Point3D, radius: float, height: float, levels_count: int = 0):

        base = RegularPolygon(base_center, radius, Cone.SIDES_COUNT)

        levels_polygons, current_level = self._get_levels_polygons(
            base.copy(), base_center.copy(), levels_count, height, radius
        )

        high = Point3D(base_center.x, base_center.y + height, base_center.z)

        center = ((high.x - base_center.x) / 2, (high.y - base_center.y) / 2, (high.y - base_center.y) / 2,)

        super().__init__(
            # Треугольники основания
            self._split_polygon_to_triangles_by_point(base, base_center) +

            # Четрырехугольники промежуточных уровней
            levels_polygons +

            # Треугольники верхушки
            self._split_polygon_to_triangles_by_point(current_level, high),
            center
        )

    @property
    def center(self) -> Point3D:
        return self.__center

    @staticmethod
    def _get_levels_polygons(current_level: RegularPolygon, current_center: Point3D,
                             levels_count: int, height: float, radius: float) -> List[Polygon]:

        levels_polygons = []

        current_radius = radius
        height_increment = height / (levels_count + 1)

        for _ in range(levels_count):
            current_center.y += height_increment
            current_radius /= 2
            new_level = RegularPolygon(current_center, current_radius, Cone.SIDES_COUNT)

            for j in range(Cone.SIDES_COUNT - 1):
                levels_polygons.append(Polygon([
                    current_level.points[j], new_level.points[j],
                    new_level.points[j + 1], current_level.points[j + 1]
                ]))

            levels_polygons.append(Polygon([
                current_level.points[-1], new_level.points[-1],
                new_level.points[0], current_level.points[0]
            ]))

            current_level = new_level

        return levels_polygons, current_level

    def _split_polygon_to_triangles_by_point(self, polygon: Polygon, point: Point3D) -> List[Polygon]:
        """
        Разбивает многоугольник на треугольники по его вершинам. Каждые две соседние
        вершины многоугольника соединяются с точкой разбиения, образуя треугольник.

        :param polygon: Разбиваемый многоугольник.
        :param point: Точка разбиения.
        :return: Массив треугольников
        """

        polygons = []

        for i in range(len(polygon.points) - 1):
            polygons.append(self._create_triangle(
                polygon.points[i], polygon.points[i + 1], point
            ))

        polygons.append(self._create_triangle(
            polygon.points[0], polygon.points[-1], point
        ))

        return polygons

    @staticmethod
    def _create_triangle(a: Point3D, b: Point3D, c: Point3D) -> Polygon:
        return Polygon([a, b, c])


class Parrallelepiped(AbstractFigure):

    def __init__(self, center: Point3D, dx: float, height: float, dz: float):
        points_bottom = [
            Point3D(center.x + dx, center.y, center.z + dz),
            Point3D(center.x - dx, center.y, center.z + dz),
            Point3D(center.x - dx, center.y, center.z - dz),
            Point3D(center.x + dx, center.y, center.z - dz),
        ]
        points_top = [Point3D(point.x, point.y + height, point.z)
                      for point in points_bottom]

        self.__top = Polygon(points_top)
        self.__bottom = Polygon(points_bottom)

    @property
    def center(self) -> Point3D:
        return avg(self.__top.points + self.__bottom.points)

    @property
    def top(self) -> Polygon:
        return self.__top

    @property
    def bottom(self) -> Polygon:
        return self.__bottom

    @property
    def side_faces(self) -> List[Polygon]:
        other = []

        for i in range(3):
            other.append(Polygon([
                self.top.points[i], self.bottom.points[i],
                self.bottom.points[i + 1], self.top.points[i + 1]
            ]))

        other.append(Polygon([
            self.top.points[-1], self.bottom.points[-1],
            self.bottom.points[0], self.top.points[0]
        ]))

        return other

    @property
    def polygons(self) -> List[Polygon]:
        return [self.bottom, self.top] + self.side_faces


class Leg(AbstractFigure):
    def __init__(self, center: Point3D, height: float):
        h_6 = height / 6
        h_3 = height / 3
        h_12 = height / 12

        parrallelepipeds = [
            Parrallelepiped(center, dx=height, dz=height, height=h_6),
            Parrallelepiped(
                Point3D(center.x, center.y + h_6, center.z),
                dx=h_3, dz=h_3, height=height / 2
            ),
            Parrallelepiped(
                Point3D(center.x, center.y + 2 * height / 3, center.z),
                dx=h_12, dz=h_12, height=h_3
            )
        ]

        self.__center = center
        self.__levels = self.__create_levels(parrallelepipeds)

    @property
    def center(self) -> Point3D:
        return self.__center

    @property
    def polygons(self) -> List[Polygon]:
        result: List[Polygon] = []

        for level in self.__levels:
            for polygon in level.polygons:
                result.append(polygon)

        return result

    @staticmethod
    def __create_levels(parrallelepipeds: List[Parrallelepiped]) -> List[BaseFigure]:
        levels = []

        for i in range(len(parrallelepipeds) - 1):
            level_top = Leg.__create_level_top(parrallelepipeds[i].top, parrallelepipeds[i + 1].bottom)
            level_polygons = [parrallelepipeds[i].bottom, *parrallelepipeds[i].side_faces, *level_top]
            level_center = avg([parrallelepipeds[i].top.center, parrallelepipeds[i + 1].bottom.center])

            levels.append(BaseFigure(level_polygons, level_center))

        last_level_center = avg([parrallelepipeds[-1].bottom.center, parrallelepipeds[-1].top.center])
        levels.append(BaseFigure([
            parrallelepipeds[-1].bottom, *parrallelepipeds[-1].side_faces
        ], last_level_center))

        return levels

    @staticmethod
    def __create_level_top(top: Polygon, bottom: Polygon) -> List[Polygon]:
        polygons = []

        for i in range(len(top.points) - 1):
            polygons.append(Polygon([
                top.points[i], bottom.points[i],
                bottom.points[i + 1], top.points[i + 1]
            ]))

        polygons.append(Polygon([
            top.points[-1], bottom.points[-1],
            bottom.points[0], top.points[0]
        ]))

        return polygons


class Spruce(AbstractFigure):
    def __init__(self, center: Point3D, height: float, radius: float, levels: int):
        self.__center = center
        self.__cone = Cone(center, radius, height, levels)

        leg_center = center.copy()
        leg_height = height / 4
        leg_center.y -= leg_height

        self.__leg = Leg(leg_center, leg_height)

    @property
    def cone(self) -> Cone:
        return self.__cone

    @property
    def leg(self) -> Leg:
        return self.__leg

    @property
    def center(self) -> Point3D:
        return self.__center

    @property
    def polygons(self) -> List[Polygon]:
        return self.__cone.polygons + self.__leg.polygons
