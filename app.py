from config import *
from game_objects.scene import TitleScene, SceneBase, GameScene
from helpers import *


def run_game(width, height, fps):
    pygame.init()
    pygame.display.set_caption("PAPER IO")
    screen = pygame.display.set_mode((width, height))
    screen.fill(CONSTS.GREY)
    clock = pygame.time.Clock()

    active_scene = TitleScene(screen,
                              'Press Enter to Start',
                              pos=(CONSTS.WINDOW_WIDTH // 2, CONSTS.WINDOW_HEIGHT // 2))
    # active_scene = GameScene(screen)
    endgame = False
    while active_scene is not None and not endgame:
        screen.fill(CONSTS.WHITE)
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False  # условие выхода из игры
            if event.type == pygame.QUIT:
                quit_attempt = True
            if quit_attempt:
                active_scene.terminate()
            else:
                filtered_events.append(event)

        active_scene.process_input(filtered_events, pressed_keys)
        status = active_scene.update()
        if status['status'] == 'endgame':
            endgame = True
        active_scene.render()

        active_scene = active_scene.next_scene

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    run_game(CONSTS.WINDOW_WIDTH, CONSTS.WINDOW_HEIGHT, CONSTS.FPS)
