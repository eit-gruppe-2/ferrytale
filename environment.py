import numpy as np
import math
import pygame
from enum import Enum
from collections import namedtuple
from itertools import product

Point = namedtuple("Point", ["x", "y"])

class Dock(pygame.sprite.Sprite):
    def __init__(self, point):
        super().__init__()
        self.image = pygame.Surface([100, 80])
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = point.x
        self.rect.y = point.y



class Position:
    point = None
    velocity = None

    def __init__(self, point, velocity):
        self.point = point
        self.velocity = velocity

    def do_action(self, velocity):
        self.velocity = velocity

    def step(self, time):
        return Point(self.point.x + time * self.velocity.x, self.point.y + time * self.velocity.y)

    def distance(self, to):
        return math.sqrt((self.point.x - to.x)**2 + (self.point.y - to.y)**2)
    


class Boat(pygame.sprite.Sprite):
    velocity = Point(0, 0)

    def __init__(self, initialPosition):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.rect = self.image.get_rect()
        self.rect.x = initialPosition.point.x
        self.rect.y = initialPosition.point.y
        self.velocity = initialPosition.velocity

    def do_action(self, action):
        x = self.velocity.x + action.horizontal_acc.value
        y = self.velocity.y + action.vertical_acc.value
        self.velocity = Point(x, y)

    def step(self, speed):
        self.position.step(speed)

    def step(self, time):
        self.rect.x = self.rect.x + time * self.velocity.x * 0.5
        self.rect.y = self.rect.y + time * self.velocity.y * 0.5

    def is_within_distance(self, distance, other_point):
        return False
        #return self.position.distance(other_point) < distance


class VerticalAccelerationChoice(Enum):
    BACK = -1
    NONE = 0
    FORWARD = 1

class HorizontalAccelerationChoice(Enum):
    LEFT = -1
    NONE = 0
    RIGHT = 1

class Action:
    horizontal_acc = HorizontalAccelerationChoice.NONE
    vertical_acc = VerticalAccelerationChoice.NONE

    def __init__(self, vertical_acc, horizontal_acc):
        self.vertical_acc = vertical_acc
        self.horizontal_acc = horizontal_acc


possibleActions = [Action(vertical_acc, horizontal_acc) for vertical_acc, horizontal_acc in product(VerticalAccelerationChoice, HorizontalAccelerationChoice)]

class Environment:

    boats = []
    goal = None
    agent = None
    speed = 1
    dimensions = [0, 0]

    def __init__(self, boats, goal, agent, speed, dimensions):
        self.boats = boats
        self.goal = goal
        self.agent = agent
        self.speed = speed
        self.dimensions = dimensions

        
    def step(self, action):

        self.agent.do_action(action)
        self.agent.step(self.speed)

        for boat in self.boats:
            boat.step(self.speed)

        nextState = None
        reward = 0
        return nextState, reward, self.is_done()

    def is_done(self):
        # Done if agent has reached goal
        agentSprite = pygame.sprite.Group()
        agentSprite.add(self.agent)
        return pygame.sprite.spritecollide(self.goal, agentSprite, False)

def position_bottom_center(dimensions):
    return Point(dimensions[0] / 2, dimensions[1])

def point_top_center(dimensions):
    return Point(dimensions[0] / 2, 0)

def point_right_center(dimensions):
    return Point(dimensions[0], dimensions[1] / 2)

# Speed: Time between frames
# Dimenstions: [width: number, height: number]
def generate_scenario(speed, dimensions):

    # Generates same environment as seen in meeting with milliampere
    agent = Boat(Position(position_bottom_center(dimensions), Point(0, -1)))

    collidable_boat = Boat(Position(point_right_center(dimensions), Point(-5, 0)))
    boats = [collidable_boat]

    goal = Dock(point_top_center(dimensions))

    return Environment(boats, goal, agent, speed, dimensions)

if __name__ == "__main__": 

    env = generate_scenario(0.16, [500, 700])

    print("Before", env.agent.rect)
    env.step(possibleActions[0])
    print("After 1", env.agent.rect)

    env.step(possibleActions[1])
    print("After 2", env.agent.rect)
