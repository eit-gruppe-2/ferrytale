"""
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/
"""
from collections import namedtuple
import pygame
import random


Size = namedtuple("Size", "width height") 
Position = namedtuple("Size", "x y") 

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (96,128,56)
RED = (255, 0, 0)
BLUE = (37,109,123)

class WaterScreen:
    def __init__(self, water_rect: pygame.Rect):
        self.water_rect = water_rect
        self.enemies = self.generateEnemies(10, water_rect)

    def generateEnemies(self, n, water_rect):
        return [EnemyBoat(Position(x, y)) for x, y in zip(random.sample(range(water_rect.left, water_rect.width), n), random.sample(range(water_rect.top, water_rect.height + water_rect.top), n))]

class EnemyBoat:
    def __init__(self, position: Position):
        self.position = position

pygame.init()

w, h = pygame.display.get_surface().get_size()
shore_height = int(h / 4)
water_rect = pygame.Rect(0, shore_height, w, h - shore_height * 2)


def draw_landscape(screen, w, h):


    # Draw shores
    pygame.draw.rect(screen, GREEN, pygame.Rect(0, 0, w, shore_height))
    pygame.draw.rect(screen, GREEN, pygame.Rect(0, h - shore_height, w, shore_height))

    # Draw water

    pygame.draw.rect(screen, BLUE, water_rect)

    return water_rect

 
def draw_enemies(screen, enemies):
    for enemy in enemies:
        pygame.draw.rect(screen, BLACK, pygame.Rect(enemy.position.x, enemy.position.y, 10, 10))

def draw_boat(screen, x, y):
    screen.blit(boat, (x, y)) 

# Setup
 
# Set the width and height of the screen [width,height]
size = Size(700, 500)

screen = pygame.display.set_mode([size.width, size.height])


pygame.display.set_caption("Ferrytale")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 

boat = pygame.image.load("./ferrytale/boat_shop.png").convert_alpha()


# Speed in pixels per frame
x_speed = 0
y_speed = 0

speed_delta = 10
 
# Current position
x_coord = 10
y_coord = 10


 
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
                x_speed = -speed_delta
            elif event.key == pygame.K_RIGHT:
                x_speed = speed_delta
            elif event.key == pygame.K_UP:
                y_speed = -speed_delta
            elif event.key == pygame.K_DOWN:
                y_speed = speed_delta
 
        # User let up on a key
        elif event.type == pygame.KEYUP:
            # If it is an arrow key, reset vector back to zero
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                x_speed = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                y_speed = 0
 
    # --- Game Logic
 
    # Move the object according to the speed vector.
    x_coord = x_coord + x_speed
    y_coord = y_coord + y_speed
 
    # --- Drawing Code
 
    # First, clear the screen to WHITE. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
 
    _ = draw_landscape(screen, w, h)
 
    waterScreen = WaterScreen(water_rect)

    draw_enemies(screen, waterScreen.enemies)
 
    draw_boat(screen, x_coord, y_coord)
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # Limit frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()