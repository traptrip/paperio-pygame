import numpy as np
import pygame
from config import *
from game_objects.player import Player


# создаем игру и окно
pygame.init()
# pygame.mixer.init()  # для звука
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # окно программы
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player1 = Player(GREEN)  # player instance
player2 = Player(RED)  # player instance
all_sprites.add(*[Player(list(np.random.random(size=3) * 256)) for i in range(1)])


# Цикл игры
running = True
while running:
    clock.tick(FPS)  # Держим цикл на правильной скорости
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(BLACK)
    all_sprites.draw(screen)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()
pygame.quit()
