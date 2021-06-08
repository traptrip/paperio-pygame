import random

import pygame


class CONSTS:
    FPS = 20  # частота кадров в секунду
    LINE_KILL_SCORE = 10
    MAX_TICK_COUNT = 1000

    # Задаем цвета
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)
    RED = (255, 0, 0, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)
    GREY = (128, 128, 128, 255)
    GOLD = (255, 225, 0, 255)
    RANDOM_COLOR = list(random.randint(0, 255) for _ in range(3)) + [255]

    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    NITRO1 = pygame.K_m

    A = pygame.K_a
    D = pygame.K_d
    W = pygame.K_w
    S = pygame.K_s
    NITRO2 = pygame.K_SPACE

    # характеристики персонажа
    SCALE = 2
    WIDTH = HEIGHT = 10 * SCALE  # ширина/высота клетки должно делиться на 2
    SHAPE = (WIDTH, WIDTH)
    # BASE_SPEED = 3
    SPEED = 1
    MOVEABLE_TICKS = 2
    NEUTRAL_TERRITORY_SCORE = 0.6
    ENEMY_TERRITORY_SCORE = 0.9

    # характеристики поля
    Y_CELLS_COUNT = 60 // SCALE
    X_CELLS_COUNT = int(1.3 * 60 // SCALE)
    GRID_HEIGHT = Y_CELLS_COUNT * HEIGHT
    GRID_WIDTH = X_CELLS_COUNT * WIDTH
    WINDOW_HEIGHT = GRID_HEIGHT
    WINDOW_WIDTH = GRID_WIDTH + 10 * WIDTH

    PLAYER_COLORS = [
        (90, 159, 153, 255),
        (216, 27, 96, 255),
        (96, 125, 139, 255),
        (245, 124, 0, 255),
        (92, 107, 192, 255),
        (141, 110, 99, 255)
    ]

    EMPTY_CELL_COLOR = (220, 240, 244, 255)
    GRID_LINE_COLOR = (144, 163, 174, 64)

    IMAGES = {
        'flash': pygame.image.load("../sprites/flash.png")
    }

    AVAILABLE_BONUSES = ['nitro', 'extra_life']
    BONUS_CHANCE = 1
    BONUSES_MAX_COUNT = 3

