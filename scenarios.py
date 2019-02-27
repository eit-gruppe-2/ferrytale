from environment import Point, Position, VisibleState, Environment, Boat, Dock, agent_image, pirate_ship_image, Shore
import pygame

def position_bottom_center(dimensions):
    return Point(dimensions[0] / 2, dimensions[1])


def point_top_center(dimensions):
    return Point(dimensions[0] / 2 - 50, -20)


def point_right_center(dimensions):
    return Point(dimensions[0], dimensions[1] / 2)


# Speed: Time between frames
# Dimenstions: [width: number, height: number]
def generate_scenario(speed, dimensions, scenario):
    if scenario == 0:
        env = simple_scenario(dimensions)
    else:
        env = long_lasting(dimensions)
    env.speed = speed
    return env


def get_defaults(dimensions):
    agent = Boat(Position(position_bottom_center(dimensions), Point(0, -1)), image=agent_image)
    goal = Dock(point_top_center(dimensions))
    shore = Shore(Point(0, -dimensions[1] + 100))
    shore.image = pygame.transform.scale(shore.image, (dimensions[0], dimensions[1]))

    return agent, goal, shore

# Generates same environment as seen in meeting with milliampere
def simple_scenario(dimensions):
    agent, goal, shore = get_defaults(dimensions)

    pirate = pygame.transform.flip(pirate_ship_image, True, False)
    collidable_boat = Boat(Position(point_right_center(dimensions), Point(-5, 0)), pirate)
    boats = [collidable_boat]


    return Environment(VisibleState(boats, goal, agent, shore), dimensions)


def long_lasting(dimensions):

    agent, goal, shore = get_defaults(dimensions)

    boats = []

    current_pos = Position(point_right_center(dimensions), Point(0, -5))
    for i in range(100):
        boats.append(Boat(Position(current_pos, Point(-5, 0)), image=None))
        new_x = current_pos.point.x + 500
        current_pos = Position(Point(new_x, current_pos.point.y), current_pos.velocity)
    
    return Environment(VisibleState(boats, goal, agent, shore), dimensions)
