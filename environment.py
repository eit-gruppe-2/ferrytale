import numpy as np
import math
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])

class Position:
    point = None
    velocity = None

    def __init__(self, point, velocity):
        self.point = point
        self.velocity = velocity

    def do_action(self, velocity):
        self.velocity = velocity

    def step(self, time):
        self.point = Point(self.point.x + time * self.velocity.x, self.point.y + time * self.velocity.y)

    def distance(self, to):
        return math.sqrt((self.point.x - to.point.x)**2 + (self.point.y - to.point.y)**2)
    


class Boat:
    position = None

    def __init__(self, initialPosition):
        self.position = initialPosition

    def do_action(self, velocity):
        self.position.velocity = velocity

    def step(self, speed):
        self.position.step(speed)


class Environment:

    boats = []
    goalPoint = None
    agent = None
    speed = 1
    dimensions = [0, 0]

    def __init__(self, boats, goalPoint, agent, speed, dimensions):
        self.boats = boats
        self.goalPoint = goalPoint
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
        done = False
        return nextState, reward, done


def position_bottom_center(dimensions):
    return Point(dimensions[0] / 2, dimensions[1])

def point_top_center(dimensions):
    return Point(dimensions[0] / 2, 0)

# Speed: Time between frames
# Dimenstions: [width: number, height: number]
def generate_scenario(speed, dimensions):
    agent = Boat(Position(position_bottom_center(dimensions), Point(0, 0)))

    boats = []

    goalPoint = Point(0, 0)

    return Environment(boats, goalPoint, agent, speed, dimensions)

if __name__ == "__main__": 

    env = generate_scenario(0.16, [500, 700])

    print("Before", env.agent.position.point)
    env.step(Point(10, 10))
    print("After 1", env.agent.position.point)

    env.step(Point(7, 7))
    print("After 2", env.agent.position.point)
