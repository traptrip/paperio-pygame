import pygame

from game_objects.player import Player, Player2
from config import CONSTS
from helpers import DrawableObj, get_random_coordinates


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
        self.background = pygame.Surface((CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT), pygame.SRCALPHA)
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
        pygame.draw.rect(self.background, self.background_color, self.background.get_rect())
        self.screen.blit(self.background, self.background.get_rect())
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
                               get_random_coordinates(),
                               CONSTS.PLAYER_COLORS[0]),
                        # Player2(2, 'player2',
                        #         (CONSTS.X_CELLS_COUNT // 3 * 2, CONSTS.Y_CELLS_COUNT // 2),
                        #         CONSTS.PLAYER_COLORS[1])
                        ]
        self.losers = []
        self.scene_status = {
            "status": 'game'
        }

    def process_input(self, events, pressed_keys):
        for player in self.players:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    player.change_direction(event.key)
                    break

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
                                         color=(255, 0, 0, 160)))
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
