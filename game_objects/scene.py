import random
import copy
from typing import Dict, List

import pygame
import pygame.freetype

from game_objects.player import Player, Player2
from game_objects.bonuses import Bonus, Nitro, ExtraLife
from game_objects.territory import Territory
from config import CONSTS
from helpers import DrawableObj, get_random_coordinates, generate_coordinates


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

    def change_image(self, image_name):
        self.block = pygame.transform.scale(CONSTS.IMAGES[image_name], (CONSTS.WIDTH, CONSTS.HEIGHT))
        self.block.set_colorkey(CONSTS.BLACK)
        self.rect = self.block.get_rect()


class StartScene(SceneBase):
    def __init__(self, screen, text, pos, color=(255, 255, 255, 255)):
        SceneBase.__init__(self, screen)
        self.text = text

        self.fontname = None
        self.headfontsize = 72
        self.pos = (pos[0], pos[1] - 2 * self.headfontsize)

        self.fontcolor = pygame.Color('black')
        self.background_color = color
        self.background = pygame.Surface((CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT), pygame.SRCALPHA)
        self.scene_status = {"status": "Menu"}

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                # Move to the next scene when the user pressed Enter
                self.switch2scene(GameScene(self.screen, game_mode='classic'))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                # Move to the next scene when the user pressed Enter
                self.switch2scene(GameScene(self.screen, game_mode='timeLIMIT'))

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.scene_status['status'] = 'endgame'

    def update(self):
        return self.scene_status

    def render(self):
        pygame.draw.rect(self.background, self.background_color, self.background.get_rect())
        self.screen.blit(self.background, self.background.get_rect())
        font = pygame.font.Font(self.fontname, self.headfontsize)
        img = font.render(self.text, True, self.fontcolor)
        rect = img.get_rect()
        rect.center = self.pos
        self.screen.blit(img, rect)

        font = pygame.font.Font(self.fontname, 42)
        img = font.render('Press 1 to start Classic Mode', True, self.fontcolor)
        rect = img.get_rect()
        rect.center = [self.pos[0], self.pos[1] + self.headfontsize]
        self.screen.blit(img, rect)

        font = pygame.font.Font(self.fontname, 42)
        img = font.render('Press 2 to start TimeLimit Mode', True, self.fontcolor)
        rect = img.get_rect()
        rect.center = [self.pos[0], self.pos[1] + self.headfontsize + 42]
        self.screen.blit(img, rect)


class EndGameScene(StartScene):
    def __init__(self, screen, text, pos, color=(255, 255, 255, 255), players=None):
        super().__init__(screen, text, pos, color)
        self.fontsize = 32
        pygame.freetype.init()
        self.font = pygame.freetype.Font(None, self.fontsize)
        self.players = players if players is not None else []

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch2scene(StartScene(self.screen,
                                             'Grab The Map',
                                             pos=(CONSTS.WINDOW_WIDTH // 2, CONSTS.GRID_HEIGHT // 2)))

    def update(self):
        return self.scene_status

    def render(self):
        self.font.render_to(self.screen,
                            (10, CONSTS.WINDOW_HEIGHT - (2 * self.fontsize)),
                            "Press Esc - open Start Page",
                            CONSTS.BLACK,
                            None, size=self.fontsize//2)

        self.font.render_to(self.screen,
                            (10, 4),
                            "SCORES",
                            CONSTS.BLACK,
                            None, size=self.headfontsize)
        for i, player in enumerate(self.players):
            if i == 0 and player.score > 0:
                self.font.render_to(self.screen,
                                    (10, self.headfontsize + 4 + i * self.fontsize),
                                    f"{player.name}: {int(player.score)}",
                                    CONSTS.GOLD,
                                    None, size=self.fontsize+2)
            else:
                self.font.render_to(self.screen,
                                    (10, self.headfontsize + 4 + i * self.fontsize),
                                    f"{player.name}: {int(player.score)}",
                                    CONSTS.BLACK,
                                    None, size=self.fontsize)


class Grid(DrawableObj):
    def __init__(self, screen):
        super().__init__(screen)
        self.grid = [[Cell(self.screen,
                           pos=(j, i),
                           color=CONSTS.EMPTY_CELL_COLOR
                           ) for j in range(0, CONSTS.GRID_WIDTH, CONSTS.WIDTH)]
                     for i in range(0, CONSTS.GRID_HEIGHT, CONSTS.HEIGHT)]

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()
        self.draw_grid_lines()

    def draw_grid_lines(self):
        for y in range(0, CONSTS.GRID_HEIGHT+1, CONSTS.HEIGHT):
            line_width = 3 if y == 0 or y == CONSTS.GRID_HEIGHT else 1
            pygame.draw.line(self.screen, CONSTS.GRID_LINE_COLOR, (0, y), (CONSTS.GRID_WIDTH, y), width=line_width)
        for x in range(0, CONSTS.GRID_WIDTH+1, CONSTS.WIDTH):
            line_width = 3 if x == 0 or x == CONSTS.GRID_WIDTH else 1
            pygame.draw.line(self.screen, CONSTS.GRID_LINE_COLOR, (x, 0), (x, CONSTS.GRID_HEIGHT), width=line_width)

    def __getitem__(self, pos):
        x, y = pos
        return self.grid[y][x]

    def __setitem__(self, pos, new_cell):
        x, y = pos
        self.grid[y][x] = new_cell


class GameScene(SceneBase):
    def __init__(self, screen, game_mode='classic'):
        SceneBase.__init__(self, screen)
        self.game_mode = game_mode
        self.tick = 0
        self.max_ticks = CONSTS.MAX_TICK_COUNT if game_mode != 'classic' else None
        self.grid = Grid(screen)
        self.available_bonuses = [Nitro]
        self.bonuses: List[Bonus] = []
        self.players = [Player(1, 'player1',
                               get_random_coordinates(),
                               CONSTS.PLAYER_COLORS[0])]
        self.players.append(Player2(2, 'player2',
                            generate_coordinates(self.players, self.get_busy_points()),
                            CONSTS.PLAYER_COLORS[1]))

        self.losers = []
        self.scene_status = {
            "status": 'game'
        }

        # text part
        self.fontname = None
        self.headfontsize = 23
        self.fontsize = 18
        self.fontcolor = pygame.Color('black')
        pygame.freetype.init()
        self.font = pygame.freetype.Font(None, self.fontsize)

    def process_input(self, events, pressed_keys):
        for player in self.players:
            for event in events:
                if event.type == pygame.KEYUP:
                    if event.key in player.extra_commands.values():
                        player.nitro(activate=False)
                if event.type == pygame.KEYDOWN:
                    if event.key in player.move_commands.values():
                        player.change_direction(event.key)
                    if event.key in player.extra_commands.values():
                        player.nitro(activate=True)

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

        # cross the line
        if (player.x, player.y) in player.line_points[:-1]:
            is_lose = True

        # line crossed by other player
        for p in players:
            if (p.x, p.y) in player.line_points[:-1]:
                if p != player:
                    p.tick_score += CONSTS.LINE_KILL_SCORE
                is_lose = True

        # if player.extra_life and is_lose:
        #     is_lose = False
        #     player.extra_life = False
        #     player.bonuses.remove([b for b in player.bonuses if b.name == 'extra_life'][0])

        # face the boarder
        if player.y < 0 or player.y >= CONSTS.Y_CELLS_COUNT or player.x < 0 or player.x >= CONSTS.X_CELLS_COUNT:
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
        for row in self.grid.grid:
            for cell in row:
                if cell.color == player.color:
                    cell.change_color(CONSTS.EMPTY_CELL_COLOR)
        try:
            for point in player.line_points[:]:
                self.grid[point].change_color(CONSTS.EMPTY_CELL_COLOR)
        except:
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
        self.__draw_bonuses()
        self.__draw_text()
        self.grid.draw()

    def __update(self):
        self.tick += 1
        for player in self.players:
            player.tick += 1
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
                self.__clear_board_from_loser(player)

        # collision resolving
        players_grabs = self.collision_resolution(players_grabs)

        # update losers list
        for player in self.players:
            is_lose, p = player.is_eaten(players_grabs)
            if is_lose:
                self.losers.append(player)
                self.__clear_board_from_loser(player)

        # update territories
        for player in self.players:
            captured = players_grabs.get(player, set())

            player.tick_action()

            for bonus in self.bonuses:
                if bonus.is_eaten(player, captured):
                    bonus.apply(player)
                    self.bonuses.remove(bonus)

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

        self.generate_bonus()

        if self.game_mode == 'timeLIMIT':
            for player in self.losers:
                player.x, player.y = generate_coordinates(self.players, self.get_busy_points())
                player.score //= 2
                player.territory = Territory(player.x, player.y, player.territory_color)
                player.line_points.clear()
                self.players.append(player)
                self.losers.remove(player)

        if self.max_ticks is not None and self.tick >= self.max_ticks:
            self.losers += self.players
            self.players = []

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

    def __draw_bonuses(self):
        for bonus in self.bonuses:
            self.grid[bonus.x, bonus.y].change_color(bonus.color)

    def __draw_text(self, ):
        self.font.render_to(self.screen,
                            (CONSTS.GRID_WIDTH + 5, 4),
                            "Players scores:",
                            CONSTS.BLACK,
                            None, size=self.headfontsize)
        for i, player in enumerate(sorted(self.players + self.losers, key=lambda x: x.score)[::-1]):
            color = CONSTS.BLACK if player in self.players else CONSTS.RED
            self.font.render_to(self.screen,
                                (CONSTS.GRID_WIDTH + 5, self.headfontsize + 4 + i * self.fontsize),
                                f"{player.name}: {int(player.score)}",
                                color,
                                None, size=self.fontsize)

        if self.game_mode == 'timeLIMIT':
            self.font.render_to(self.screen,
                                (CONSTS.GRID_WIDTH + 5, CONSTS.WINDOW_HEIGHT - 20),
                                f"Ticks left: {self.max_ticks - self.tick}",
                                CONSTS.BLACK,
                                None, size=self.fontsize)

    def __update_scene_status(self):
        if not any([any([self.grid[x, y].color == CONSTS.EMPTY_CELL_COLOR
                         for x in range(CONSTS.X_CELLS_COUNT)])
                    for y in range(CONSTS.Y_CELLS_COUNT)]):
            self.switch2scene(StartScene(self.screen,
                                         f"SUPER WINNER: {self.players[0].name}",
                                         pos=(CONSTS.GRID_WIDTH // 2, CONSTS.GRID_HEIGHT // 2),
                                         color=CONSTS.WHITE))

        if len(self.players) <= 1:
            self.switch2scene(EndGameScene(self.screen,
                                           f"ENDGAME",
                                           pos=(CONSTS.WINDOW_WIDTH // 2, CONSTS.WINDOW_HEIGHT // 2),
                                           color=CONSTS.WHITE,
                                           players=sorted(self.players, key=lambda x: x.score)[::-1] +
                                                   sorted(self.losers, key=lambda x: x.score)[::-1]))
        return self.scene_status

    def get_busy_points(self):
        players_points = {(p.x, p.y) for p in self.players}
        bonuses_points = {(b.x, b.y) for b in self.bonuses}
        territory_points = set()
        for p in self.players:
            territory_points |= {i for i in p.territory.points}
        lines_points = set()
        for player in self.players:
            lines_points |= {i for i in player.line_points}

        return players_points | bonuses_points | lines_points | territory_points

    def generate_bonus(self):
        if len(self.available_bonuses) > 0:
            if random.randint(1, CONSTS.BONUS_CHANCE) == 1 and len(self.bonuses) < CONSTS.BONUSES_MAX_COUNT:
                coors = generate_coordinates(self.players, self.get_busy_points())
                bonus = random.choice(self.available_bonuses)(coors)
                self.bonuses.append(bonus)
