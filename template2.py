import pygame
from pygame.locals import *

from config import *
from game_objects.player import Player
from game_objects.scene import TitleScene, SceneBase, GameScene
from helpers import *


# class SceneBase:
#     def __init__(self):
#         self.next_scene = self
#
#     def process_input(self, events, pressed_keys):
#         print("uh-oh, you didn't override this in the child class")
#
#     def update(self):
#         print("uh-oh, you didn't override this in the child class")
#
#     def render(self, screen):
#         print("uh-oh, you didn't override this in the child class")
#
#     def switch2scene(self, next_scene):
#         self.next_scene = next_scene
#
#     def terminate(self):
#         self.switch2scene(None)


# class TitleScene(SceneBase):
#     def __init__(self, text, pos):
#         SceneBase.__init__(self)
#         self.text = text
#         self.pos = pos
#
#         self.fontname = None
#         self.fontsize = 72
#         self.fontcolor = Color('black')
#
#     def process_input(self, events, pressed_keys):
#         for event in events:
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
#                 # Move to the next scene when the user pressed Enter
#                 self.switch2scene(GameScene())
#
#     def update(self):
#         pass
#
#     def render(self, screen):
#         # For the sake of brevity, the title scene is a blank red screen
#         font = pygame.font.Font(self.fontname, self.fontsize)
#         img = font.render(self.text, True, self.fontcolor)
#         rect = img.get_rect()
#         rect.center = self.pos
#         screen.blit(img, rect)


# class GameScene(SceneBase):
#     def __init__(self):
#         SceneBase.__init__(self)
#         self.player = Player(CONSTS.GREEN)
#         self.all_sprites = pygame.sprite.Group()
#         self.all_sprites.add(self.player)
#
#     def process_input(self, events, pressed_keys):
#         pass
#
#     def update(self):
#         self.all_sprites.update()
#
#     def render(self, screen):
#         # The game scene is just a blank blue screen
#         screen.fill(CONSTS.BLACK)
#         draw_grid(CONSTS.WINDOW_WIDTH, CONSTS.X_CELLS_COUNT, screen)
#         # self.player.draw(screen)
#         self.all_sprites.draw(screen)
#         screen.blit(pygame.Surface((150, 150)), (0, 0))



# def draw_grid(width, rows, surface):
#     cell_size = width // rows  # Gives us the distance between the lines
#     x = y = 0  # Keeps track of the current x, y
#     for _ in range(rows):  # We will draw one vertical and one horizontal line each loop
#         x += cell_size
#         y += cell_size
#         pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, width))
#         pygame.draw.line(surface, (255, 255, 255), (0, y), (width, y))


def run_game(width, height, fps):
    pygame.init()
    pygame.display.set_caption("PAPER IO")
    screen = pygame.display.set_mode((width, height))
    screen.fill(Color('gray'))
    clock = pygame.time.Clock()

    active_scene = TitleScene(screen,
                              'Press Enter to Start',
                              pos=(CONSTS.WINDOW_WIDTH // 2, CONSTS.WINDOW_HEIGHT // 2))
    # active_scene = GameScene(screen)

    while active_scene is not None:
        screen.fill(Color('gray'))
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False  # условие выхода из игры
            if event.type == pygame.QUIT:
                quit_attempt = True
            if quit_attempt:
                active_scene.terminate()
            else:
                filtered_events.append(event)

        active_scene.process_input(filtered_events, pressed_keys)
        active_scene.update()
        active_scene.render()

        active_scene = active_scene.next_scene

        pygame.display.flip()
        clock.tick(fps)


run_game(CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT, CONSTS.FPS)
