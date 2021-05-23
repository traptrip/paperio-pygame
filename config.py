import os
import random

import pygame


class CONSTS:
    FPS = 10  # частота кадров в секунду
    LINE_KILL_SCORE = 10
    MAX_TICK_COUNT = 2000

    # Задаем цвета
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RANDOM_COLOR = tuple(random.randint(0, 255) for _ in range(3))

    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN

    # характеристики персонажа
    WIDTH = HEIGHT = 20  # ширина/высота клетки должно делиться на 2
    SHAPE = (WIDTH, WIDTH)
    # BASE_SPEED = 3
    SPEED = 1

    # характеристики поля
    Y_CELLS_COUNT = 30
    X_CELLS_COUNT = 30
    WINDOW_HEIGHT = Y_CELLS_COUNT * WIDTH
    WINDOW_WIDTH = X_CELLS_COUNT * WIDTH

    PLAYER_COLORS = [
        (90, 159, 153, 255),
        (216, 27, 96, 255),
        (96, 125, 139, 255),
        (245, 124, 0, 255),
        (92, 107, 192, 255),
        (141, 110, 99, 255)
    ]

    EMPTY_CELL_COLOR = (10, 10, 10)
    GRID_LINE_COLOR = (128, 128, 128)

    IMAGES = {
        'flash': pygame.image.load("../sprites/flash.png")
    }

    TERRITORY_CACHE = {}
