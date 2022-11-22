from typing import List

from graphics.figures import BaseFigure, AbstractFigure
from graphics.help_functions import avg, cyclic_pare_iter
from graphics.polygons import RegularPolygon, Triangle, Rectangle, BasePolygon
from graphics.types import Point3D


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

    @staticmethod
    def _get_levels_polygons(current_level: RegularPolygon, current_center: Point3D,
                             levels_count: int, height: float, radius: float) -> List[BasePolygon]:

        levels_polygons = []

        current_radius = radius
        height_increment = height / (levels_count + 1)

        for _ in range(levels_count):
            current_center.y += height_increment
            current_radius /= 2
            new_level = RegularPolygon(current_center, current_radius, Cone.SIDES_COUNT)

            for j1, j2 in cyclic_pare_iter(range(Cone.SIDES_COUNT)):
                levels_polygons.append(BasePolygon([
                    current_level.points[j1], new_level.points[j1],
                    new_level.points[j2], current_level.points[j2]
                ]))

            current_level = new_level

        return levels_polygons, current_level

    @staticmethod
    def _split_polygon_to_triangles_by_point(polygon: BasePolygon, split_point: Point3D) -> List[Triangle]:
        """
        Разбивает многоугольник на треугольники по его вершинам. Каждые две соседние
        вершины многоугольника соединяются с точкой разбиения, образуя треугольник.

        :param polygon: Разбиваемый многоугольник.
        :param split_point: Точка разбиения.
        :return: Массив треугольников
        """

        return [
            Triangle(p_cur, p_next, split_point)
            for p_cur, p_next in cyclic_pare_iter(polygon.points)
        ]


class Parrallelepiped(AbstractFigure):

    def __init__(self, center: Point3D, dx: float, height: float, dz: float):

        points_bottom = [
            Point3D(center.x + dx, center.y, center.z - dz),
            Point3D(center.x + dx, center.y, center.z + dz),
            Point3D(center.x - dx, center.y, center.z - dz),
            Point3D(center.x - dx, center.y, center.z + dz),
        ]

        points_top = [
            Point3D(point.x, point.y + height, point.z)
            for point in points_bottom
        ]

        self.__top = Rectangle(*points_top)
        self.__bottom = Rectangle(*points_bottom)
        self.__side_faces = [
            Rectangle(
                self.top.points[i_cur], self.top.points[i_next],
                self.bottom.points[i_cur], self.bottom.points[i_next], False
            ) for i_cur, i_next in cyclic_pare_iter(range(4))
        ]

    @property
    def center(self) -> Point3D:
        return avg(self.__top.points + self.__bottom.points)

    @property
    def top(self) -> Rectangle:
        return self.__top

    @property
    def bottom(self) -> Rectangle:
        return self.__bottom

    @property
    def side_faces(self) -> List[Rectangle]:
        return self.__side_faces

    @property
    def polygons(self) -> List[Rectangle]:
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
    def polygons(self) -> List[BasePolygon]:
        result: List[BasePolygon] = []

        for level in self.__levels:
            for polygon in level.polygons:
                result.append(polygon)

        return result

    @staticmethod
    def __create_levels(parrallelepipeds: List[Parrallelepiped]) -> List[BaseFigure]:
        levels = []

        for i in range(len(parrallelepipeds) - 1):
            level_top = Leg.__create_level_top(parrallelepipeds[i].top, parrallelepipeds[i + 1].bottom)

            # Разделить "стенки" основания на маленькие части
            splitted_side_faces = []
            for side_face in parrallelepipeds[i].side_faces:
                for splited_side_face in side_face.split(12):
                    splitted_side_faces.append(splited_side_face)

            level_polygons = [
                parrallelepipeds[i].bottom,
                *level_top,
                *splitted_side_faces
            ]

            level_center = avg([parrallelepipeds[i].top.center, parrallelepipeds[i + 1].bottom.center])
            levels.append(BaseFigure(level_polygons, level_center))

        last_level_center = avg([parrallelepipeds[-1].bottom.center, parrallelepipeds[-1].top.center])
        levels.append(BaseFigure([
            parrallelepipeds[-1].bottom, *parrallelepipeds[-1].side_faces
        ], last_level_center))

        # Разбиение основания на маленькие квадратики
        base = levels[0].polygons.pop(0)
        for rect in Leg._split_square(base):
            for sub_rect in Leg._split_square(rect):
                for sub_sub_rect in Leg._split_square(sub_rect):
                    levels[0].polygons.append(sub_sub_rect)

        return levels

    @staticmethod
    def _split_square(square: BasePolygon) -> List[BasePolygon]:
        l = square.points[0].distance_between(square.points[1]) / 2
        halfs = [
            Point3D(square.center.x, square.center.y, square.center.z + l),
            Point3D(square.center.x + l, square.center.y, square.center.z + l),
            Point3D(square.center.x + l, square.center.y, square.center.z),
            Point3D(square.center.x + l, square.center.y, square.center.z - l),
            Point3D(square.center.x, square.center.y, square.center.z - l),
            Point3D(square.center.x - l, square.center.y, square.center.z - l),
            Point3D(square.center.x - l, square.center.y, square.center.z),
            Point3D(square.center.x - l, square.center.y, square.center.z + l),
        ]

        a = []

        for i in range(0, len(halfs), 2):
            last_i = i + 2 if i != len(halfs) - 2 else 0
            a.append(BasePolygon([
                halfs[i], halfs[i + 1], halfs[last_i], square.center
            ]))

        return a

    @staticmethod
    def __create_level_top(top: BasePolygon, bottom: BasePolygon) -> List[Triangle]:
        polygons = []

        for cur_i, next_i in cyclic_pare_iter(range(len(top.points))):

            top_center = (top.points[cur_i] + top.points[next_i]) / 2

            polygons += Triangle(top.points[cur_i], bottom.points[cur_i], top_center).split()
            polygons += Triangle(bottom.points[cur_i], top_center, bottom.points[next_i]).split()
            polygons += Triangle(top_center, bottom.points[next_i], top.points[next_i]).split()

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
    def polygons(self) -> List[BasePolygon]:
        return self.__cone.polygons + self.__leg.polygons
