import random
from config import CONSTS


def get_random_coordinates():
    return random.randint(CONSTS.SHAPE[0], CONSTS.WINDOW_WIDTH - CONSTS.SHAPE[0]), \
           random.randint(CONSTS.SHAPE[0], CONSTS.WINDOW_HEIGHT - CONSTS.SHAPE[0])


class Painter:
    """Used to organize the drawing / updating procedure. (FIFO)"""

    def __init__(self):
        self.paintings = []

    def add(self, drawable_obj):
        self.paintings.append(drawable_obj)

    def paint(self):
        for drawing in self.paintings:
            drawing.draw()


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


def in_polygon(x, y, xp, yp):
    """
    :param x: point x coordinate
    :param y: point y coordinate
    :param xp: array of other x coords
    :param yp: array of other y coords
    :return: True if point is inside the polygon else False
    """
    is_inside = False
    for i in range(len(xp)):
        if ((yp[i] <= y < yp[i - 1]) or (yp[i - 1] <= y < yp[i])) and \
                (x > (xp[i - 1] - xp[i]) * (y - yp[i]) / (yp[i - 1] - yp[i]) + xp[i]):
            is_inside = not is_inside

    return is_inside
