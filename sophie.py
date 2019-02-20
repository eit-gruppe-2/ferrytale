import pygame
pygame.init()


# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE=(0,128,180)


# class ferry(pygame.sprite.Sprite):
#     def __init__(self):
#         pygame.sprite.Sprite.__init__(self)
#         ferry.rect = rect()

def draw_stick_figure(screen, x, y):

    screen.fill(BLUE)
    pygame.draw.rect(screen, BLACK, [1 + x, y, 20, 20], 0)

def draw_boat(boat, x, y):
    pygame.draw.rect(boat, GREEN, [x, y, 20, 20], 0)

# Set the width and height of the screen [width,height]

display_width = 700
display_height = 500

size = [display_width, display_height]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Ferrytale")


# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Hide the mouse cursor
pygame.mouse.set_visible(0)

xb = 450
yb = 0



# Speed in pixels per frame
x_speed = 0
y_speed = 0
speed = 3
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

    # while not crashed:
    #for event in pygame.event.get()


    # --- Game Logic

    # Move the object according to the speed vector.
    x_coord = x_coord + x_speed
    y_coord = y_coord + y_speed

    yb = yb + speed

    if yb == 480:
        speed = - speed

    if yb == 0:
        speed = -speed

    if x_coord == xb:
        done = True
    elif y_coord == yb:
        done = True

    # y_prev= 0
    #
    # while y_prev <= yb:
    #     y_prev = yb
    #     yb = yb + 3
    #     if yb == 480:
    #         yb = yb - 3
    #
    # while y_prev > yb:
    #      y_prev = yb
    #      yb = yb - 3
    #      if yb == 0:
    #         y_prev = yb - 1


    if x_coord < 0:
        x_coord = 0
    elif x_coord > 680:
        x_coord = 680
    if y_coord < 0:
        y_coord = 0
    elif y_coord > 480:
        y_coord = 480

    # --- Drawing Code

    # First, clear the screen to WHITE. Don't put other drawing commands
    # above this, or they will be erased with this command.


    draw_stick_figure(screen, x_coord, y_coord)

    draw_boat(screen, xb, yb)


    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()