import random
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from config import CONSTS


def get_random_coordinates():
    return random.randint(CONSTS.X_CELLS_COUNT // 4, CONSTS.X_CELLS_COUNT - (CONSTS.X_CELLS_COUNT // 4)), \
           random.randint(CONSTS.Y_CELLS_COUNT // 4, CONSTS.Y_CELLS_COUNT - (CONSTS.Y_CELLS_COUNT // 4))


class DrawableObj:
    """Abstract base-class for every drawable element."""

    def __init__(self, screen):
        self.screen = screen

    def draw(self, *args, **kwargs):
        pass


# TERRITORY HELPERS
def get_diagonal_neighbours(point):
    x, y = point
    return [
        (x + 1, y + 1),
        (x - 1, y + 1),
        (x + 1, y - 1),
        (x - 1, y - 1)
    ]


def get_vert_and_horiz_neighbours(point):
    x, y = point
    return [
        (x, y + 1),
        (x - 1, y),
        (x, y - 1),
        (x + 1, y),
    ]


def get_neighboring_points(point):
    """
    Get vertical, horizontal and diagonal neighbour points of current point
    """
    return [
        *get_vert_and_horiz_neighbours(point),
        *get_diagonal_neighbours(point)
    ]


def in_polygon(x, y, boundary):
    """
    :param x: point x coordinate
    :param y: point y coordinate
    :param boundary: a polygon
    :return: True if point is inside the polygon else False
    """
    point = Point(x, y)
    polygon = Polygon(boundary)
    is_inside = polygon.contains(point)

    return is_inside


def is_available_point(x, y, players, busy_points):
    for p in players:
        if (p.x - 4 <= x <= p.x + 4) and (p.y - 4 <= y <= p.y + 4):
            return False
    return (x, y) not in busy_points


def generate_coordinates(players, busy_points):
    x, y = get_random_coordinates()
    while not is_available_point(x, y, players, busy_points):
        x, y = get_random_coordinates()
    return x, y

