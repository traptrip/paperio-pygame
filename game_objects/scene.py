import copy
from typing import Dict, List

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
                        Player2(2, 'player2',
                                (CONSTS.X_CELLS_COUNT // 3 * 2, CONSTS.Y_CELLS_COUNT // 2),
                                CONSTS.PLAYER_COLORS[1])
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

    @staticmethod
    def collision_resolution(players_grabs: Dict[Player, set]):
        pg = {player: grab for player, grab in players_grabs.items() if not player.is_eaten(players_grabs)[0]}
        res_pg = {player: copy.copy(grab) for player, grab in pg.items()}
        for player1, captured1 in pg.items():
            for player2, captured2 in pg.items():
                if player1 != player2:
                    res_pg[player1].difference_update(captured2)  # remove captured2 from first players grabs
        return res_pg

    @staticmethod
    def is_player_lose(player: Player, players: List[Player]):
        is_lose = False

        # face the boarder or cross the line
        if player.y < 0 or player.y >= CONSTS.Y_CELLS_COUNT or player.x < 0 or player.x >= CONSTS.X_CELLS_COUNT or \
                (player.x, player.y) in player.line_points[:-1]:
            is_lose = True

        # line crossed by other player
        for p in players:
            if (p.x, p.y) in player.line_points[:-1]:
                if p != player:
                    p.tick_score += CONSTS.LINE_KILL_SCORE
                is_lose = True

        # faced with other player
        for p in players:
            if (player.x, player.y) == (p.x, p.y) and p != player:
                if len(player.line_points) >= len(p.line_points):  # win player with longer line
                    is_lose = True

        # if player lost his territory
        if len(player.territory.points) == 0:
            is_lose = True

        return is_lose

    def __clear_board_from_loser(self, player: Player):
        # clear the head and line points
        for point in player.line_points[:-1]:
            self.grid[point].change_color(CONSTS.EMPTY_CELL_COLOR)
        # clear territory
        for point in player.territory.points:
            self.grid[point].change_color(CONSTS.EMPTY_CELL_COLOR)

    def update(self):
        status = self.__update_scene_status()
        self.__update()
        return status

    def render(self):
        for player in self.players:
            self.__draw_player_territory(player)
        for player in self.players:
            self.__draw_player_head(player)
            self.__draw_player_line(player)
        self.grid.draw()

    def __update(self):
        for p in self.players:
            p.tick += 1
        # move players
        for player in self.players:
            if player.tick % player.moveable_tick == 0:
                player.move()

        # count captured territories
        players_grabs = {}
        for player in self.players:
            if player.tick % player.moveable_tick == 0:
                player.update_line()
                captured = player.territory.capture(player.line_points)
                players_grabs[player] = captured
                if len(captured) > 0:
                    player.line_points.clear()
                    player.tick_score += CONSTS.NEUTRAL_TERRITORY_SCORE * len(captured)

        # catch losers
        for player in self.players:
            is_lose = self.is_player_lose(player, self.players)
            if is_lose:
                self.losers.append(player)

        # collision resolving
        players_grabs = self.collision_resolution(players_grabs)

        # update losers list
        for player in self.players:
            is_lose, p = player.is_eaten(players_grabs)
            if is_lose:
                self.losers.append(player)

        # update territories
        for player in self.players:
            captured = players_grabs.get(player, set())

            # player.tick_action()

            if captured:
                player.territory.points.update(captured)
                for p in self.players:
                    if p != player:
                        removed = p.territory.remove_points(captured)
                        player.tick_score += \
                            (CONSTS.ENEMY_TERRITORY_SCORE - CONSTS.NEUTRAL_TERRITORY_SCORE) * len(removed)

        # remove losers from players list
        for player in self.losers:
            if player in self.players:
                self.players.remove(player)
                self.__clear_board_from_loser(player)

        # update players scores
        for player in self.players:
            player.score += player.tick_score
            player.tick_score = 0

    def __draw_player_territory(self, player):
        for point in player.territory.points:
            self.grid[point].change_color(player.territory.color)
            self.grid[point].prev_color = player.territory.color

    def __draw_player_line(self, player):
        for point in player.line_points:
            if point != (player.x, player.y):
                self.grid[point].change_color(player.line_color)

    def __draw_player_head(self, player):
        if player.prev_x is not None:
            self.grid[player.prev_x, player.prev_y].change_color(self.grid[player.prev_x, player.prev_y].prev_color)
        self.grid[player.x, player.y].change_color(player.color)

    def __update_scene_status(self):
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

        # if len(self.players) == 1:
        #     self.switch2scene(TitleScene(self.screen,
        #                                  f"WINNER: {self.players[0].name}",
        #                                  pos=(CONSTS.WINDOW_WIDTH // 2, CONSTS.WINDOW_HEIGHT // 2),
        #                                  color=CONSTS.WHITE))
        return self.scene_status