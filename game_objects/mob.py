# import random
# import pygame
# from config import *
#
#
# class Mob(pygame.sprite.Sprite):
#     def __init__(self, color):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.Surface(SHAPE)
#         self.image.fill(color)
#         self.rect = self.image.get_rect()
#         self.rect.center = (random.randint(SHAPE[0], WIDTH-SHAPE[0]),
#                             random.randint(SHAPE[0], HEIGHT-SHAPE[0]))
#         self.base_speed = BASE_SPEED
#         self.speed_x = BASE_SPEED
#         self.speed_y = 0
#
#     def update(self):
#         key_state = pygame.key.get_pressed()  # pressed key
#         self.__update_base_speed(key_state)
#         self.__update_player_speed(key_state)
#
#         self.rect.x += self.speed_x
#         self.rect.y += self.speed_y
#
#         if self.rect.left > WIDTH:
#             self.rect.right = 0
#         if self.rect.right < 0:
#             self.rect.left = WIDTH - 1
#         if self.rect.top > HEIGHT:
#             self.rect.top = 0
#         if self.rect.bottom < 0:
#             self.rect.bottom = HEIGHT - 1
#
#     def __update_base_speed(self, key_state):
#         if key_state[pygame.K_SPACE]:
#             self.base_speed = BASE_SPEED + 10
#         else:
#             self.base_speed = BASE_SPEED
#
#     def __update_player_speed(self, key_state):
#         if key_state[pygame.K_LEFT]:
#             self.speed_y = 0
#             self.speed_x = -self.base_speed
#         if key_state[pygame.K_RIGHT]:
#             self.speed_y = 0
#             self.speed_x = self.base_speed
#         if key_state[pygame.K_UP]:
#             self.speed_x = 0
#             self.speed_y = -self.base_speed
#         if key_state[pygame.K_DOWN]:
#             self.speed_x = 0
#             self.speed_y = self.base_speed
#         else:
#             self.speed_x = self.base_speed if self.speed_x > 0 else -self.base_speed if self.speed_x < 0 else 0
#             self.speed_y = self.base_speed if self.speed_y > 0 else -self.base_speed if self.speed_y < 0 else 0
#
#
