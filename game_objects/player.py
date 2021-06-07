from copy import copy
from game_objects.territory import Territory
from config import CONSTS


class Player:
    direction = None

    def __init__(self, player_id, name, pos, color):
        self.id = player_id
        self.x = self.prev_x = pos[0]
        self.y = self.prev_y = pos[1]
        self.player_commands = {
            'up': CONSTS.UP,
            'down': CONSTS.DOWN,
            'left': CONSTS.LEFT,
            'right': CONSTS.RIGHT
        }
        # color of player's head
        self.color = [i - 35 if i >= 35 else i for i in color[:-1]] + [color[-1]]
        # color of the player tail outside the territory
        self.line_color = list(color[:-1]) + [150]
        # captured territory
        self.territory = Territory(self.x, self.y, color)
        # player lines outside the territory
        self.line_points = []
        self.name = name
        self.score = 0
        self.tick_score = 0
        self.direction = self.player_commands['up']
        self.tick = 0
        self.moveable_tick = CONSTS.MOVEABLE_TICKS
        self.speed = CONSTS.SPEED

    def change_direction(self, command):
        true_dir = self.__get_true_direction()
        if command == self.player_commands['up'] and true_dir != 'down':
            self.direction = self.player_commands['up']

        elif command == self.player_commands['down'] and true_dir != 'up':
            self.direction = self.player_commands['down']

        elif command == self.player_commands['left'] and true_dir != 'right':
            self.direction = self.player_commands['left']

        elif command == self.player_commands['right'] and true_dir != 'left':
            self.direction = self.player_commands['right']

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
        if self.direction == self.player_commands['up']:
            self.y -= self.speed
        elif self.direction == self.player_commands['down']:
            self.y += self.speed
        elif self.direction == self.player_commands['left']:
            self.x -= self.speed
        elif self.direction == self.player_commands['right']:
            self.x += self.speed

    def update_line(self):
        if (self.x, self.y) not in self.territory.points or len(self.line_points) > 0:
            self.line_points.append((self.x, self.y))

    def get_state(self):
        return {
            'score': self.score,
            'direction': self.direction,
            'territory': list(self.territory.points),
            'lines': copy(self.line_points),
            'position': (self.x, self.y),
        }

    def get_state_for_event(self):
        return {
            'id': self.id,
            'direction': self.direction,
            'lines_length': len(self.line_points),
            'position': (self.x, self.y),
        }

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


class Player2(Player):
    def __init__(self, player_id, name, pos, color):
        super().__init__(player_id, name, pos, color)
        self.player_commands = {
            'up': CONSTS.W,
            'down': CONSTS.S,
            'left': CONSTS.A,
            'right': CONSTS.D
        }
        self.direction = self.player_commands['up']

    # def move(self):
    #     if self.direction == self.player_commands['up']:
    #         self.y -= 0
    #     elif self.direction == self.player_commands['down']:
    #         self.y += 0
    #     elif self.direction == self.player_commands['left']:
    #         self.x -= 0
    #     elif self.direction == self.player_commands['right']:
    #         self.x += 0
    #
    #     # check death collisions
    #     if self.y < 0 or self.y >= CONSTS.Y_CELLS_COUNT or self.x < 0 or self.x >= CONSTS.X_CELLS_COUNT or \
    #             (self.x, self.y) in self.line_points:
    #         if self.y < 0:
    #             self.y += 1
    #         if self.y >= CONSTS.Y_CELLS_COUNT:
    #             self.y -= 1
    #         if self.x < 0:
    #             self.x += 1
    #         if self.x >= CONSTS.X_CELLS_COUNT:
    #             self.x -= 1
    #         self.kill_player()
