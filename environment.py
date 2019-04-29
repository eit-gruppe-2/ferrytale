import math
import pygame
from enum import Enum
from itertools import product
from collections import namedtuple

# Define a named point touple.
Point = namedtuple("Point", ["x", "y"])

# Load the images for the game objects.
agent_image = pygame.image.load("./assets/boat_shop.png")
dock_image = pygame.image.load("./assets/dock.png")
pirate_ship_image = pygame.image.load("./assets/PirateShip.png")
kayak_image = pygame.image.load("./assets/kayak.png")
grass_image = pygame.image.load("./assets/grass.png")


# Class containing the different rewards.
class Rewards(Enum):
    BOAT_CRASH = -1
    WALL_CRASH = -1
    GRASS_CRASH = -1
    GOAL_HIT = 10
    GOT_CLOSER = 2
    ALMOST_THERE = 3
    LIVING = -0.1


# Class describing the dock.
class Dock(pygame.sprite.Sprite):
    def __init__(self, point):
        super().__init__()
        self.image = dock_image 
        self.rect = self.image.get_rect()
        self.rect.x = point.x
        self.rect.y = point.y


# Class describing the shorelines.
class Shore(pygame.sprite.Sprite):
    def __init__(self, point):
        super().__init__()
        self.image = grass_image
        self.rect = self.image.get_rect()
        self.rect.x = point.x
        self.rect.y = point.y


# Class describing position and velocity.
class Position:
    def __init__(self, point, velocity):
        self.point = point
        self.velocity = velocity


# Class describing the boats.
class Boat(pygame.sprite.Sprite):
    def __init__(self, initial_position, image=None):
        super().__init__()

        if image is not None:
            self.image = image
        else:
            self.image = pygame.Surface([40, 40])

        self.rect = self.image.get_rect()
        self.rect.x = initial_position.point.x
        self.rect.y = initial_position.point.y
        self.velocity = initial_position.velocity

    def do_action(self, action):
        x = self.velocity.x + action.horizontal_acc.value
        y = self.velocity.y + action.vertical_acc.value
        if x > 10:
            x = 10
        elif x < -10:
            x = -10
        if y > 10:
            y = 10
        elif y < -10:
            y = -10
        self.velocity = Point(x, y)

    # Move the boat one time step.
    def step(self, time):
        self.rect.x = self.rect.x + time * self.velocity.x * 0.5
        self.rect.y = self.rect.y + time * self.velocity.y * 0.5


# Class describing vertical acceleration for the action choices.
class VerticalAccelerationChoice(Enum):
    BACK = -1
    NONE = 0
    FORWARD = 1


# Class describing horizontal acceleration for the action choices.
class HorizontalAccelerationChoice(Enum):
    LEFT = -1
    NONE = 0
    RIGHT = 1


# Class describing the resulting vertical and horizontal acceleration from an action.
class Action:
    def __init__(self, vertical_acc, horizontal_acc):
        self.vertical_acc = vertical_acc
        self.horizontal_acc = horizontal_acc


# List of all possible actions.
possibleActions = [Action(vertical_acc, horizontal_acc) for vertical_acc, horizontal_acc in
                   product(VerticalAccelerationChoice, HorizontalAccelerationChoice)]


# Class describing the visible game state.
class VisibleState:
    def __init__(self, boats, goal, agent, top_shore, bottom_shore):
        self.boats = boats
        self.goal = goal
        self.agent = agent
        self.top_shore = top_shore
        self.bottom_shore = bottom_shore


# Function calculating the distance between two pygame rects.
def rect_distance(rect1, rect2):
    x1a, y1a = rect1.topleft
    x1b, y1b = rect1.bottomright
    x2a, y2a = rect2.topleft
    x2b, y2b = rect2.bottomright
    left = x2b < x1a
    right = x1b < x2a
    top = y2b < y1a
    bottom = y1b < y2a
    if bottom and left:
        return math.hypot(x2b - x1a, y2a - y1b)
    elif left and top:
        return math.hypot(x2b - x1a, y2b - y1a)
    elif top and right:
        return math.hypot(x2a - x1b, y2b - y1a)
    elif right and bottom:
        return math.hypot(x2a - x1b, y2a - y1b)
    elif left:
        return x1a - x2b
    elif right:
        return x2a - x1b
    elif top:
        return y1a - y2b
    elif bottom:
        return y2a - y1b
    else:
        # The rects intersect.
        return 0.


# Class describing the main game environment.
class Environment:
    def __init__(self, visible_state, dimensions, speed=1):
        self.state = visible_state
        self.speed = speed
        self.dimensions = dimensions
        self.given_rewards = []

    # Function translating a choice by the agent to an in-game action.
    @staticmethod
    def index_to_action(index):
        num_actions = len(possibleActions)
        if index >= num_actions or index < 0:
            raise Exception("Index was outside the range of possible indices. Has to be between 0 and", num_actions - 1)
        return possibleActions[index]

    # Function that advances the game by one time step.
    def step(self, action):
        self.state.agent.do_action(action)
        self.state.agent.step(self.speed)

        for boat in self.state.boats:
            boat.step(self.speed)

        next_state = self.state
        reward, done = self.get_reward() 
        return next_state, reward, done

    # Function that checks for collisions in the game.
    def collisions(self):
        collidable_sprites = pygame.sprite.Group()
        collidable_sprites.add(self.state.top_shore)
        collidable_sprites.add(self.state.bottom_shore)
        collidable_sprites.add(self.state.goal)
        collidable_sprites.add(self.state.boats)

        collisions = pygame.sprite.spritecollide(self.state.agent, collidable_sprites, False)
        number_of_collisions = len(collisions)
        col_reward = 0

        # Check for collisions between ferry and goal, boats and grass.
        for collision in collisions:
            if collision == self.state.goal:
                col_reward = Rewards.GOAL_HIT.value
            if collision in self.state.boats:
                col_reward += Rewards.BOAT_CRASH.value
            if collision == self.state.top_shore or collision == self.state.bottom_shore:
                col_reward += Rewards.GRASS_CRASH.value
            
        # Check to see if the ferry leaves the game area.
        inside_screen = True
        if not pygame.Rect(0, 0, self.dimensions[0], self.dimensions[1]).contains(self.state.agent.rect):
            inside_screen = False
            col_reward += Rewards.WALL_CRASH.value

        return number_of_collisions > 0 or not inside_screen, col_reward

    # Function for rewarding the agent.
    def get_reward(self):
        done, reward = self.collisions()

        # There are checkpoints halfway and three quarters of the way from the starting position to the dock.
        # Check if the ferry crossed either of these and make sure it's only rewarded once for each checkpoint.
        if Rewards.GOT_CLOSER not in self.given_rewards and \
                self.get_distance_between_agent_goal() < self.dimensions[0] / 2:
            reward += Rewards.GOT_CLOSER.value
            self.given_rewards.append(Rewards.GOT_CLOSER)

        if Rewards.ALMOST_THERE not in self.given_rewards and \
                self.get_distance_between_agent_goal() < self.dimensions[0] / 4:
            reward += Rewards.ALMOST_THERE.value
            self.given_rewards.append(Rewards.ALMOST_THERE)

        # Subtract a small amount of points for being alive to combat passiveness.
        if not done:
            reward += Rewards.LIVING.value

        return reward, done

    # Function for calling the rect_distance function.
    def get_distance_between_agent_goal(self):
        return rect_distance(self.state.agent.rect, self.state.goal.rect)
