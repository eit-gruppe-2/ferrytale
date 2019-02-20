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


xb = 450
yb = 0
x_coord = 10
y_coord = 10

environment = env.generate_scenario(0.16,[700,500])

display_width = 700
display_height = 500
size = [display_width, display_height]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Ferrytale")

boat_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()

boat = Ferry(GREEN, 20, 20)
boat.rect.x = xb
boat.rect.y = yb

boat_list.add(boat)
all_sprites_list.add(boat)

myboat = Ferry(BLACK,20,20)
myboat.rect.x = x_coord
myboat.rect.y = y_coord
all_sprites_list.add(myboat)


def ourboat(screen, x, y):
    pygame.draw.rect(screen, BLACK, [1 + x, y, 20, 20], 0)

def draw_boat(boat, x, y):
    pygame.draw.rect(boat, GREEN, [x, y, 20, 20], 0)

# Set the width and height of the screen [width,height]




# Loop until the user clicks the close button.
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
                x_speed = -3
            elif event.key == pygame.K_RIGHT:
                x_speed = 3
            elif event.key == pygame.K_UP:
                y_speed = -3
            elif event.key == pygame.K_DOWN:
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
    draw_boat(screen,environment.agent.position.point.x,environment.agent.position.point.y)
    environment.step(env.Point(0.1,0.1))

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()
