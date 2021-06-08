from copy import copy
from game_objects.territory import Territory
from config import CONSTS


class Player:
    direction = None

    def __init__(self, player_id, name, pos, color):
        self.id = player_id
        self.name = name
        self.x = self.prev_x = pos[0]
        self.y = self.prev_y = pos[1]
        self.move_commands = {
            'up': CONSTS.UP,
            'down': CONSTS.DOWN,
            'left': CONSTS.LEFT,
            'right': CONSTS.RIGHT,
        }
        self.extra_commands = {
            'nitro': CONSTS.NITRO1
        }
        # color of player's head
        self.color = [i - 35 if i >= 35 else i for i in color[:-1]] + [color[-1]]
        self.territory_color = color
        # color of the player tail outside the territory
        self.line_color = list(color[:-1]) + [150]
        # captured territory
        self.territory = Territory(self.x, self.y, color)
        # player lines outside the territory
        self.line_points = []

        self.score = 0
        self.tick_score = 0
        self.direction = self.move_commands['up']
        self.tick = 0

        # bonuses
        self.moveable_tick = CONSTS.MOVEABLE_TICKS
        self.extra_life = False
        self.bonuses = []

    def change_direction(self, command):
        true_dir = self.__get_true_direction()
        if command == self.move_commands['up'] and true_dir != 'down':
            self.direction = self.move_commands['up']

        elif command == self.move_commands['down'] and true_dir != 'up':
            self.direction = self.move_commands['down']

        elif command == self.move_commands['left'] and true_dir != 'right':
            self.direction = self.move_commands['left']

        elif command == self.move_commands['right'] and true_dir != 'left':
            self.direction = self.move_commands['right']

    def __get_true_direction(self):
        x_dir = self.x - self.prev_x
        y_dir = self.y - self.prev_y
        if x_dir > 0:
            return 'right'
        elif x_dir < 0:
            return 'left'
        else:
            if y_dir > 0:
                return 'down'
            elif y_dir < 0:
                return 'up'
        return None

    def move(self):
        self.prev_x, self.prev_y = self.x, self.y
        if self.direction == self.move_commands['up']:
            self.y -= 1
        elif self.direction == self.move_commands['down']:
            self.y += 1
        elif self.direction == self.move_commands['left']:
            self.x -= 1
        elif self.direction == self.move_commands['right']:
            self.x += 1

    def update_line(self):
        if (self.x, self.y) not in self.territory.points or len(self.line_points) > 0:
            self.line_points.append((self.x, self.y))

    def get_position(self):
        return self.x, self.y

    def is_eaten(self, players_grabs):
        """
        :param players_grabs: captured territories for all players
        :return: True if player has been eaten by other player, player that eat this player or None
        """
        for p, captured in players_grabs.items():
            position = self.get_position()
            if self != p and position in captured:
                return True, p
        return False, None

    def nitro(self, activate=True):
        for bonus in self.bonuses:
            if bonus.name == 'Nitro':
                bonus.activated = activate
                if activate:
                    self.moveable_tick = 1
                else:
                    bonus.cancel(self)

    def tick_action(self):
        for bonus in self.bonuses:
            if bonus.name == 'Nitro' and bonus.activated:
                bonus.tick += 1
                if bonus.tick >= bonus.active_ticks:
                    bonus.cancel(self)
                    self.bonuses.remove(bonus)


class Player2(Player):
    def __init__(self, player_id, name, pos, color):
        super().__init__(player_id, name, pos, color)
        self.move_commands = {
            'up': CONSTS.W,
            'down': CONSTS.S,
            'left': CONSTS.A,
            'right': CONSTS.D,
        }
        self.extra_commands = {
            'nitro': CONSTS.NITRO2
        }
        self.direction = self.move_commands['up']

    # def move(self):
    #     pass
