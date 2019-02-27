import pygame
import os, sys
import time
from tkinter import *
from tkinter import messagebox
import environment as env

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


pygame.init()


def run_game():
    display_width = 700
    display_height = 500

    env_speed = 1
    env_dim = [display_width, display_height]
    environment = env.generate_scenario(env_speed, env_dim)
    size = [display_width, display_height]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Ferrytale")

    boat_list = pygame.sprite.Group()
    dock = pygame.sprite.Group()
    all_sprites_list = pygame.sprite.Group()
    all_sprites_list.add(environment.goal)
    all_sprites_list.add(environment.agent)
    boat_list.add(environment.boats)
    all_sprites_list.add(environment.boats)

    NO_ACTION = env.Action(env.VerticalAccelerationChoice.NONE, env.HorizontalAccelerationChoice.NONE)

    done = False
    clock = pygame.time.Clock()
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

        nextState, reward, env_done, collision = environment.step(NO_ACTION)

        if collision:
            Tk().wm_withdraw()  # to hide the main window
            messagebox.showinfo('Continue', 'Du har kollidert')
            return True

        if env_done:
            environment = env.generate_scenario(env_speed, env_dim)
            return True
        pygame.display.flip()

        # Limit frames per second
        clock.tick(60)

    return False


restart = True
while restart:
    restart = run_game()
pygame.quit()