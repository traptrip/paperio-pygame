import pygame

from game_objects.player import Player, Player2
from config import CONSTS
from helpers import DrawableObj


class SceneBase:
    def __init__(self, screen):
        self.screen = screen
        self.next_scene = self

    def process_input(self, events, pressed_keys):
        NotImplementedError("uh-oh, you didn't override this in the child class")

    def update(self):
        NotImplementedError("uh-oh, you didn't override this in the child class")

    def render(self):
        NotImplementedError("uh-oh, you didn't override this in the child class")

    def switch2scene(self, next_scene):
        self.next_scene = next_scene

    def terminate(self):
        self.switch2scene(None)


class Cell(DrawableObj):
    def __init__(self, screen, pos=(0, 0), color=(0, 0, 0, 255), image_name=None):
        super().__init__(screen)
        self.color = color
        self.prev_color = color
        self.image_name = image_name
        if image_name is not None:
            self.block = pygame.transform.scale(CONSTS.IMAGES[image_name], (CONSTS.WIDTH, CONSTS.HEIGHT))
        else:
            self.block = pygame.Surface((CONSTS.WIDTH, CONSTS.HEIGHT), pygame.SRCALPHA)
        self.block.set_colorkey(CONSTS.BLACK)
        self.rect = self.block.get_rect()
        self.rect.topleft = pos
        self.pos = pos

    def draw(self):
        pygame.draw.rect(self.block, self.color, self.block.get_rect())
        self.screen.blit(self.block, self.rect)

    def change_color(self, new_color):
        self.color = new_color


class TitleScene(SceneBase):
    def __init__(self, screen, text, pos, color=(255, 255, 255, 255)):
        SceneBase.__init__(self, screen)
        self.text = text
        self.pos = pos

        self.fontname = None
        self.fontsize = 72
        self.fontcolor = pygame.Color('black')
        self.background_color = color
        self.scene_status = {"status": "Menu"}

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.switch2scene(GameScene(self.screen))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.scene_status['status'] = 'endgame'

    def update(self):
        return self.scene_status

    def render(self):
        self.screen.fill(self.background_color)
        font = pygame.font.Font(self.fontname, self.fontsize)
        img = font.render(self.text, True, self.fontcolor)
        rect = img.get_rect()
        rect.center = self.pos
        self.screen.blit(img, rect)


class Grid(DrawableObj):
    def __init__(self, screen):
        super().__init__(screen)
        self.grid = [[Cell(self.screen,
                           pos=(j, i),
                           color=CONSTS.EMPTY_CELL_COLOR
                           ) for j in range(0, CONSTS.WINDOW_WIDTH, CONSTS.WIDTH)]
                     for i in range(0, CONSTS.WINDOW_HEIGHT, CONSTS.HEIGHT)]

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()
        self.draw_grid_lines()

    def draw_grid_lines(self):
        for y in range(CONSTS.HEIGHT, CONSTS.WINDOW_HEIGHT, CONSTS.HEIGHT):
            pygame.draw.line(self.screen, CONSTS.GRID_LINE_COLOR, (0, y), (CONSTS.WINDOW_WIDTH, y))
        for x in range(CONSTS.WIDTH, CONSTS.WINDOW_WIDTH, CONSTS.WIDTH):
            pygame.draw.line(self.screen, CONSTS.GRID_LINE_COLOR, (x, 0), (x, CONSTS.WINDOW_HEIGHT))

    def __getitem__(self, pos):
        x, y = pos
        return self.grid[y][x]

    def __setitem__(self, pos, new_cell):
        x, y = pos
        self.grid[y][x] = new_cell


class GameScene(SceneBase):
    def __init__(self, screen):
        SceneBase.__init__(self, screen)
        self.grid = Grid(screen)
        self.players = [Player(1, 'player1',
                               (CONSTS.X_CELLS_COUNT // 3, CONSTS.Y_CELLS_COUNT // 2),
                               CONSTS.PLAYER_COLORS[0]),
                        Player2(2, 'player2',
                                (CONSTS.X_CELLS_COUNT // 3 * 2, CONSTS.Y_CELLS_COUNT // 2),
                                CONSTS.PLAYER_COLORS[1])
                        ]
        self.losers = []
        self.scene_status = {
            "status": 'game'
        }

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                for player in self.players:
                    player.change_direction(event.key)

    def update(self):
        status = self.__update_scene_status()
        self.__update_grid()
        return status

    def render(self):
        self.grid.draw()

    def __update_grid(self):
        for player in self.players:
            self.__update_territory(player)
            self.__update_player(player)
            self.__update_player_lines(player)

    def __update_territory(self, player: Player):
        captured = player.territory.capture(player.line_points)
        if len(captured) > 0:
            player.line_points.clear()
            self.__update_score(player, len(captured))
            player.territory.points.update(captured)

        for point in player.territory.points:
            self.grid[point].change_color(player.territory.color)
            self.grid[point].prev_color = player.territory.color

    @staticmethod
    def __update_score(player: Player, captured_length):
        player.tick_score += CONSTS.NEUTRAL_TERRITORY_SCORE * captured_length

    def __update_player(self, player: Player):
        # player head
        prev_player_x, prev_player_y = player.x, player.y
        player.move()
        self.grid[prev_player_x, prev_player_y].change_color(self.grid[prev_player_x, prev_player_y].prev_color)
        self.grid[player.x, player.y].change_color(player.color)

    def __update_player_lines(self, player: Player):
        # player lines
        player.update_line()
        for point in player.line_points:
            if point != (player.x, player.y):
                self.grid[point].change_color(player.line_color)

    def __update_scene_status(self):
        for player in self.players:
            if not player.is_alive:
                self.losers.append(player)
                self.players.remove(player)
                self.__clear_board_from_player(player)
        if not self.players:
            self.switch2scene(TitleScene(self.screen,
                                         "GAME OVER",
                                         pos=(CONSTS.WINDOW_WIDTH // 2, CONSTS.WINDOW_HEIGHT // 2),
                                         color=CONSTS.RED))
        if not any([any([self.grid[x, y].color == CONSTS.EMPTY_CELL_COLOR
                         for x in range(CONSTS.X_CELLS_COUNT)])
                    for y in range(CONSTS.Y_CELLS_COUNT)]):
            self.switch2scene(TitleScene(self.screen,
                                         f"WINNER: {self.players[0].name}",
                                         pos=(CONSTS.WINDOW_WIDTH // 2, CONSTS.WINDOW_HEIGHT // 2),
                                         color=CONSTS.WHITE))
        return self.scene_status

    def __clear_board_from_player(self, player: Player):
        # clear the head and line points
        for point in player.line_points:
            self.grid[point].change_color(CONSTS.EMPTY_CELL_COLOR)
        # clear territory
        for point in player.territory.points:
            self.grid[point].change_color(CONSTS.EMPTY_CELL_COLOR)



    # background_color = (220 / 255, 240 / 255, 244 / 255, 1)
    # border_color = (144, 163, 174, 255)
    # grid_color = (144, 163, 174, 64)
    # border_width = 2
    # game_over_label_color = (95, 99, 104, 255)
    #
    # leaderboard_color = (255, 255, 255, 128)
    # leaderboard_width = 320
    # leaderboard_height = 240
    #
    # leaderboard_rows_count = 0
    # labels_buffer = []
    #
    # def __init__(self):
    #     self.game_over_label = pygame.text.Label('GAME OVER', font_name='Times New Roman',
    #                                              font_size=30,
    #                                              color=self.game_over_label_color,
    #                                              x=CONSTS.WINDOW_WIDTH / 2, y=CONSTS.WINDOW_HEIGHT / 2,
    #                                              anchor_x='center', anchor_y='center')
    #
    # def clear(self):
    #     self.window.clear()
    #     self.draw_grid()
    #
    # def append_label_to_leaderboard(self, label, color):
    #     if len(self.labels_buffer) > self.leaderboard_rows_count:
    #         self.labels_buffer[self.leaderboard_rows_count].text = label
    #         self.labels_buffer[self.leaderboard_rows_count].color = color
    #     else:
    #         self.labels_buffer.append(
    #             pyglet.text.Label(label,
    #                               font_name='Times New Roman',
    #                               font_size=16,
    #                               color=color,
    #                               x=CONSTS.WINDOW_WIDTH - self.leaderboard_width + 20,
    #                               y=CONSTS.WINDOW_HEIGHT - 20 - CONSTS.WIDTH / 2 - 30 * self.leaderboard_rows_count,
    #                               anchor_x='left', anchor_y='center')
    #         )
    #     self.leaderboard_rows_count += 1
    #
    # def reset_leaderboard(self):
    #     self.leaderboard_rows_count = 0
    #
    # def show_game_over(self, timeout=False):
    #     self.game_over_label.text = 'TIMEOUT' if timeout else 'GAME OVER'
    #     self.game_over_label.draw()
    #
    # def draw_grid(self):
    #     self.grid.draw()
    #
    # def draw_border(self):
    #     draw_line((0, 0), (0, CONSTS.WINDOW_HEIGHT), self.border_color, self.border_width)
    #     draw_line((0, CONSTS.WINDOW_HEIGHT), (CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT), self.border_color, self.border_width)
    #     draw_line((CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT), (CONSTS.WINDOW_WIDTH, 0), self.border_color, self.border_width)
    #     draw_line((CONSTS.WINDOW_WIDTH, 0), (0, 0), self.border_color, self.border_width)
    #
    # def draw_leaderboard(self):
    #     draw_quadrilateral((CONSTS.WINDOW_WIDTH - self.leaderboard_width, CONSTS.WINDOW_HEIGHT - self.leaderboard_height,
    #                         CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT - self.leaderboard_height,
    #                         CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT,
    #                         CONSTS.WINDOW_WIDTH - self.leaderboard_width, CONSTS.WINDOW_HEIGHT),
    #                        self.leaderboard_color)
    #     for label in self.labels_buffer[:self.leaderboard_rows_count]:
    #         label.draw()
    #     self.reset_leaderboard()
    #
    #
    #
