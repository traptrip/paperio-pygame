import pygame

from config import CONSTS
from helpers import get_random_coordinates


# class Player(pygame.sprite.Sprite):
#     def __init__(self, color):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.Surface(CONSTS.SHAPE)
#         self.image.fill(color)
#         self.rect = self.image.get_rect()
#         self.rect.center = get_random_coordinates()
#
#         self.base_speed = CONSTS.SPEED
#         self.speed_x = CONSTS.SPEED
#         self.speed_y = 0
#
#         self.bonuses = []
#
#     def update(self):
#         key_state = pygame.key.get_pressed()  # pressed key
#         self.__update_base_speed(key_state)
#         self.__move(key_state)
#
#         self.rect.x += self.speed_x
#         self.rect.y += self.speed_y
#
#         if self.rect.left > CONSTS.WINDOW_WIDTH:
#             self.rect.right = 0
#         if self.rect.right < 0:
#             self.rect.left = CONSTS.WINDOW_WIDTH - 1
#         if self.rect.top > CONSTS.WINDOW_HEIGHT:
#             self.rect.top = 0
#         if self.rect.bottom < 0:
#             self.rect.bottom = CONSTS.WINDOW_HEIGHT - 1
#
#     def __update_base_speed(self, key_state):
#         if key_state[pygame.K_SPACE]:
#             self.base_speed = CONSTS.SPEED + 10
#         else:
#             self.base_speed = CONSTS.SPEED
#
#     def __move(self, key_state):
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


from copy import copy
from game_objects.territory import Territory
from config import CONSTS
from helpers import batch_draw, draw_square


class Player:
    direction = None

    def __init__(self, player_id, name, pos, color):
        self.id = player_id
        self.x = pos[0]
        self.y = pos[1]
        self.color = [i - 25 if i >= 25 else i for i in color[:-1]] + [color[-1]]
        self.line_color = list(color[:-1]) + [160]  # color of the player tail outside the territory
        self.territory = Territory(self.x, self.y, color)  # captured territory
        self.lines = []  # player lines outside the territory
        self.name = name
        self.score = 0
        self.tick_score = 0
        self.direction = CONSTS.UP

        # self.client = client
        # self.is_disconnected = False
        self.speed = CONSTS.SPEED

    def change_direction(self, command):
        if command == CONSTS.UP and self.direction != CONSTS.DOWN:
            self.direction = CONSTS.UP

        elif command == CONSTS.DOWN and self.direction != CONSTS.UP:
            self.direction = CONSTS.DOWN

        elif command == CONSTS.LEFT and self.direction != CONSTS.RIGHT:
            self.direction = CONSTS.LEFT

        elif command == CONSTS.RIGHT and self.direction != CONSTS.LEFT:
            self.direction = CONSTS.RIGHT

    def move(self):
        if self.direction == CONSTS.UP:
            self.y -= self.speed
        elif self.direction == CONSTS.DOWN:
            self.y += self.speed
        elif self.direction == CONSTS.LEFT:
            self.x -= self.speed
        elif self.direction == CONSTS.RIGHT:
            self.x += self.speed

        if self.y < 0:
            self.y = CONSTS.Y_CELLS_COUNT - 1
        if self.y >= CONSTS.Y_CELLS_COUNT:
            self.y = 0
        if self.x < 0:
            self.x = CONSTS.X_CELLS_COUNT - 1
        if self.x >= CONSTS.X_CELLS_COUNT:
            self.x = 0



    def draw_lines(self):
        batch_draw(self.lines, self.line_color)

    def draw_position(self):
        draw_square((self.x, self.y), self.color)

    def update_lines(self):
        if (self.x, self.y) not in self.territory.points or len(self.lines) > 0:
            self.lines.append((self.x, self.y))

    def tick_action(self): ...
        # for bonus in self.bonuses[:]:
        #     bonus.tick += 1
        #
        #     if bonus.tick >= bonus.active_ticks:
        #         bonus.cancel(self)
        #         self.bonuses.remove(bonus)

    def get_state(self):
        return {
            'score': self.score,
            'direction': self.direction,
            'territory': list(self.territory.points),
            'lines': copy(self.lines),
            'position': (self.x, self.y),
            # 'bonuses': self.get_bonuses_state()
        }

    def get_state_for_event(self):
        return {
            'id': self.id,
            'direction': self.direction,
            'lines_length': len(self.lines),
            'position': (self.x, self.y),
        }

    @staticmethod
    def get_command():
        command = pygame.event.get()[0].type
        return command if command else None

    def _get_line(self, dx, dy):
        x, y = self.x, self.y
        points = []
        while 0 < x < CONSTS.WIDTH and 0 < y < CONSTS.HEIGHT:
            x += dx
            y += dy
            points.append((x, y))
        return points

    def get_direction_line(self):
        if self.direction == CONSTS.UP:
            return self._get_line(0, CONSTS.WIDTH)

        if self.direction == CONSTS.DOWN:
            return self._get_line(0, -CONSTS.WIDTH)

        if self.direction == CONSTS.LEFT:
            return self._get_line(-CONSTS.WIDTH, 0)

        if self.direction == CONSTS.RIGHT:
            return self._get_line(CONSTS.WIDTH, 0)

    def diff_position(self, direction, x, y, val):
        if direction == CONSTS.UP:
            return x, y - val

        if direction == CONSTS.DOWN:
            return x, y + val

        if direction == CONSTS.LEFT:
            return x + val, y

        if direction == CONSTS.RIGHT:
            return x - val, y

    def get_position(self):
        if self.direction is None:
            return self.x, self.y

        x, y = self.x, self.y
        while not ((x - round(CONSTS.WIDTH / 2)) % CONSTS.WIDTH == 0 and
                   (y - round(CONSTS.WIDTH / 2)) % CONSTS.WIDTH == 0):
            x, y = self.diff_position(self.direction, x, y, self.speed)

        return (x, y), (x, y) != (self.x, self.y)

    def get_prev_position(self):
        if self.direction is None:
            return self.x, self.y
        return self.diff_position(self.direction, self.x, self.y, CONSTS.WIDTH)

    def is_ate(self, players_to_captured):
        for p, captured in players_to_captured.items():
            position, is_move = self.get_position()
            if self != p and position in captured and (is_move or self.get_prev_position() in captured):
                return True, p
        return False, None


