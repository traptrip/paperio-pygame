from typing import List

import pygame

from helpers import DrawableObj
from game_objects.player import Player


class HeadUpDisplay(DrawableObj):
    """Represent all necessary Head-Up Display information on screen.
    """

    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font(None, 20)

    def draw(self, players: List[Player]):
        pass
