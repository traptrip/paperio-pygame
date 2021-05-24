from copy import copy
from game_objects.territory import Territory
from config import CONSTS


class Player:
    direction = None

    def __init__(self, player_id, name, pos, color):
        self.id = player_id
        self.x = pos[0]
        self.y = pos[1]
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

        self.speed = CONSTS.SPEED
        self.is_alive = True

    def change_direction(self, command):
        if command == self.player_commands['up'] and self.direction != self.player_commands['down']:
            self.direction = self.player_commands['up']

        elif command == self.player_commands['down'] and self.direction != self.player_commands['up']:
            self.direction = self.player_commands['down']

        elif command == self.player_commands['left'] and self.direction != self.player_commands['right']:
            self.direction = self.player_commands['left']

        elif command == self.player_commands['right'] and self.direction != self.player_commands['left']:
            self.direction = self.player_commands['right']

    def move(self):
        if self.direction == self.player_commands['up']:
            self.y -= self.speed
        elif self.direction == self.player_commands['down']:
            self.y += self.speed
        elif self.direction == self.player_commands['left']:
            self.x -= self.speed
        elif self.direction == self.player_commands['right']:
            self.x += self.speed

        if self.y < 0 or self.y >= CONSTS.Y_CELLS_COUNT or self.x < 0 or self.x >= CONSTS.X_CELLS_COUNT:
            if self.y < 0:
                self.y += 1
            if self.y >= CONSTS.Y_CELLS_COUNT:
                self.y -= 1
            if self.x < 0:
                self.x += 1
            if self.x >= CONSTS.X_CELLS_COUNT:
                self.x -= 1
            self.kill_player()

    def update_line(self):
        if (self.x, self.y) not in self.territory.points or len(self.line_points) > 0:
            self.line_points.append((self.x, self.y))

    def tick_action(self): ...
        # for bonus in self.bonuses[:]:
        #     bonus.tick += 1
        #
        #     if bonus.tick >= bonus.active_ticks:
        #         bonus.cancel(self)
        #         self.bonuses.remove(bonus)

    def kill_player(self):
        self.is_alive = False
        # self.territory.points.clear()
        # self.line_points.clear()

    def get_state(self):
        return {
            'score': self.score,
            'direction': self.direction,
            'territory': list(self.territory.points),
            'lines': copy(self.line_points),
            'position': (self.x, self.y),
            # 'bonuses': self.get_bonuses_state()
        }

    def get_state_for_event(self):
        return {
            'id': self.id,
            'direction': self.direction,
            'lines_length': len(self.line_points),
            'position': (self.x, self.y),
        }

    def is_ate(self, players_to_captured):
        for p, captured in players_to_captured.items():
            position, is_move = self.get_position()
            if self != p and position in captured and (is_move or self.get_prev_position() in captured):
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
