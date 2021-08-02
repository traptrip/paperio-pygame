from game_objects.player import Player
from helpers import get_random_coordinates, is_available_point
from config import CONSTS


class Bonus:
    image_path = None
    color = None
    name = None
    activated = False

    def __init__(self, point):
        x, y = point
        self.x = x
        self.y = y
        self.tick = 0
        self.active_ticks = self.generate_active_ticks()

    @staticmethod
    def generate_active_ticks():
        return 10  # random.choice([i * 10 for i in range(1, 6)])

    def is_eaten(self, player: Player, captured):
        return (self.x, self.y) == (player.x, player.y) or (self.x, self.y) in captured

    def get_remaining_ticks(self):
        return self.active_ticks - self.tick

    def cancel(self, player: Player):
        pass

    def apply(self, player: Player):
        pass

    def activate(self, player):
        pass


class Nitro(Bonus):
    color = (255, 249, 0, 255)
    image_path = 'sprites/flash.png'
    name = 'Nitro'
    activated = False

    def apply(self, player):
        b = [b for b in player.bonuses if type(b) == type(self)]
        if len(b) > 0:
            b[0].active_ticks += self.active_ticks
        else:
            player.bonuses.append(self)

    def cancel(self, player):
        player.moveable_tick = CONSTS.MOVEABLE_TICKS


class ExtraLife(Bonus):
    color = (234, 10, 10, 255)
    image_path = 'sprites/hart.png'
    name = 'extra_life'

    def apply(self, player):
        player.bonuses.append(self)
        player.extra_life = True

    def cancel(self, player):
        player.extra_life = False
