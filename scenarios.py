import enum
import pygame
from random import choice, randint
from environment import Point, Position, VisibleState, Environment, Boat, Dock, agent_image, pirate_ship_image,\
    kayak_image, Shore


# Function for calculating the coordinates of the bottom center of the screen for spawning the ferry.
def point_bottom_center(dimensions):
    return Point(dimensions[0] / 2, dimensions[1] - 100)


# Function for calculating the coordinates of the top center of the screen for positioning the dock.
def point_top_center(dimensions):
    return Point(dimensions[0] / 2 - 50, -20)


# Function for calculating the coordinates of the right center of the screen for spawning the boats.
def point_right_center(dimensions):
    return Point(dimensions[0], dimensions[1] / 2)


# Function for resizing boat images.
def resize(ratio, surface):
    return pygame.transform.scale(surface, (round(surface.get_width() * ratio), round(surface.get_height() * ratio)))


# Function for generating scenarios of boat traffic: simple or more complex.
def generate_scenario(speed, dimensions, scenario):
    if scenario == ScenarioType.SIMPLE:
        env = simple_scenario(dimensions)
    elif scenario == ScenarioType.COMPLEX:
        env = complex_scenario(dimensions)
    env.speed = speed
    return env


# Function for placing the incoming boats, dock and shores correctly.
def get_defaults(dimensions):
    agent = Boat(Position(point_bottom_center(dimensions), Point(0, -1)), image=agent_image)
    goal = Dock(point_top_center(dimensions))
    top_shore = Shore(Point(0, -dimensions[1] + 50))
    top_shore.image = pygame.transform.scale(top_shore.image, (dimensions[0], dimensions[1]))
    bot_shore = Shore(Point(0, dimensions[1] - 20))
    bot_shore.image = pygame.transform.scale(top_shore.image, (dimensions[0], dimensions[1]))
    return agent, goal, top_shore, bot_shore


# Enumerator containing the two scenario types.
class ScenarioType(enum.Enum):
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"


# Function for generating a simple scenario with one boat.
def simple_scenario(dimensions):
    agent, goal, top_shore, bot_shore = get_defaults(dimensions)

    pirate = pygame.transform.flip(pirate_ship_image, True, False)
    collidable_boat = Boat(Position(point_right_center(dimensions), Point(-5, 0)), pirate)
    boats = [collidable_boat]

    return Environment(VisibleState(boats, goal, agent, top_shore, bot_shore), dimensions)


# Function for generating a more complex scenario with multiple types of boats.
def complex_scenario(dimensions):
    agent, goal, top_shore, bot_shore = get_defaults(dimensions)

    boats = []
    pirate = resize(0.5, pygame.transform.flip(pirate_ship_image, True, False))
    kayak = resize(0.1, kayak_image)
    possible_boats = [pirate, kayak]

    center_y = point_right_center(dimensions).y
    current_pos = Position(point_right_center(dimensions), Point(-randint(10, 13), 0))

    # Spawn 10 boats.
    for _ in range(10):
        boats.append(Boat(current_pos, image=choice(possible_boats)))
        new_x = current_pos.point.x + randint(200, 1000)
        new_y = center_y + randint(-50, 50)
        velocity = Point(-randint(10, 13), 0)
        current_pos = Position(Point(new_x, new_y), velocity)
    
    return Environment(VisibleState(boats, goal, agent, top_shore, bot_shore), dimensions)
