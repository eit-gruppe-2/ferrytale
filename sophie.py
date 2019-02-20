import pygame
import os, sys
import time
import environment as env

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE=(0,128,180)


class Ferry(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

pygame.init()

display_width = 700
display_height = 500

env_speed = 1
env_dim = [display_width, display_height]
environment = env.generate_scenario(env_speed, env_dim)

xb = 450
yb = 0
x_coord = 10
y_coord = 10

size = [display_width, display_height]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Ferrytale")

boat_list = pygame.sprite.Group()
dock = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()
all_sprites_list.add(environment.goal)
boat = Ferry(GREEN, 20, 20)
boat.rect.x = xb
boat.rect.y = yb

boat_list.add(boat)
all_sprites_list.add(boat)

myboat = Ferry(BLACK,20,20)
myboat.rect.x = x_coord
myboat.rect.y = y_coord
all_sprites_list.add(myboat)
all_sprites_list.add(environment.agent)
boat_list.add(environment.boats)
all_sprites_list.add(environment.boats)

NO_ACTION = env.Action(env.VerticalAccelerationChoice.NONE, env.HorizontalAccelerationChoice.NONE)

def ourboat(screen, x, y):
     pygame.draw.rect(screen, BLACK, [1 + x, y, 20, 20], 0)

def draw_boat(boat, x, y):
     pygame.draw.rect(boat, GREEN, [x, y, 20, 20], 0)

done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Hide the mouse cursor
pygame.mouse.set_visible(0)


# Speed in pixels per frame
x_speed = 0
y_speed = 0
speed = 3
# Current position


# -------- Main Program Loop -----------
while not done:
    # --- Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            # User pressed down on a key

        elif event.type == pygame.KEYDOWN:
            # Figure out if it was an arrow key. If so
            # adjust speed.
            if event.key == pygame.K_LEFT:
                environment.step(env.Action(env.VerticalAccelerationChoice.NONE, env.HorizontalAccelerationChoice.LEFT))
                x_speed = -3
            elif event.key == pygame.K_RIGHT:
                environment.step(env.Action(env.VerticalAccelerationChoice.NONE, env.HorizontalAccelerationChoice.RIGHT))
                x_speed = 3
            elif event.key == pygame.K_UP:
                environment.step(env.Action(env.VerticalAccelerationChoice.BACK, env.HorizontalAccelerationChoice.NONE))
                y_speed = -3
            elif event.key == pygame.K_DOWN:
                environment.step(env.Action(env.VerticalAccelerationChoice.FORWARD, env.HorizontalAccelerationChoice.NONE))
                y_speed = 3

        # User let up on a key
        elif event.type == pygame.KEYUP:
            # If it is an arrow key, reset vector back to zero
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                x_speed = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                y_speed = 0
        


    x_coord = x_coord + x_speed
    y_coord = y_coord + y_speed

    yb = yb + speed

    if yb == 480:
        speed = - speed
    if yb == 0:
        speed = -speed


    if x_coord < 0:
        x_coord = 0
    elif x_coord > 680:
        x_coord = 680
    if y_coord < 0:
        y_coord = 0
    elif y_coord > 480:
        y_coord = 480

    myboat.rect.x = x_coord
    myboat.rect.y = y_coord
    boat.rect.x = xb
    boat.rect.y = yb
    if pygame.sprite.spritecollide(myboat, boat_list, True):
        done = True

    screen.fill(BLUE)
    all_sprites_list.draw(screen)
    draw_boat(screen, xb, yb)

    nextState, reward, env_done = environment.step(NO_ACTION)

    if env_done:
        environment = env.generate_scenario(env_speed, env_dim)
    pygame.display.flip()

    # Limit frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()
