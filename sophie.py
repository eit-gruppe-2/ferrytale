import pygame
import os, sys
import time
import environment as env
from scenarios import generate_scenario

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 128, 180)


class Ferry(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()


def text_to_screen(screen, text, x, y, size=30,
                   color=(24, 45, 62), font_type='Helvetica'):
    text = str(text)
    font = pygame.font.SysFont(font_type, size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))


pygame.init()


def run_game():
    display_width = 1100
    display_height = 800

    env_speed = 1
    env_dim = [display_width, display_height]
    environment = generate_scenario(env_speed, env_dim, 0)

    size = [display_width, display_height]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Ferrytale")

    boat_list = pygame.sprite.OrderedUpdates()
    all_sprites_list = pygame.sprite.Group()
    all_sprites_list.add(environment.state.top_shore)
    all_sprites_list.add(environment.state.goal)
    all_sprites_list.add(environment.state.agent)
    boat_list.add(environment.state.boats)
    all_sprites_list.add(environment.state.boats)

    NO_ACTION = env.Action(env.VerticalAccelerationChoice.NONE, env.HorizontalAccelerationChoice.NONE)

    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Hide the mouse cursor
    pygame.mouse.set_visible(0)


    # -------- Main Program Loop -----------
    while not done:
        # --- Event Processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    environment.step(
                        env.Action(env.VerticalAccelerationChoice.NONE, env.HorizontalAccelerationChoice.LEFT))

                elif event.key == pygame.K_RIGHT:
                    environment.step(
                        env.Action(env.VerticalAccelerationChoice.NONE, env.HorizontalAccelerationChoice.RIGHT))

                elif event.key == pygame.K_UP:
                    environment.step(
                        env.Action(env.VerticalAccelerationChoice.BACK, env.HorizontalAccelerationChoice.NONE))

                elif event.key == pygame.K_DOWN:
                    environment.step(
                        env.Action(env.VerticalAccelerationChoice.FORWARD, env.HorizontalAccelerationChoice.NONE))


        screen.fill(BLUE)
        all_sprites_list.draw(screen)

        nextState, reward, env_done = environment.step(NO_ACTION)

        if env_done:
            return True

        text_to_screen(screen, "Reward {0}".format(round(reward)), display_width - 160, display_height - 50)
        pygame.display.flip()

        # Limit frames per second
        clock.tick(60)

    return False


restart = True
while restart:
    restart = run_game()

# Close the window and quit.
pygame.quit()