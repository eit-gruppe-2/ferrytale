import pygame
import os, sys
import time
import numpy as np
from random import randint
from deepQ import DQNAgent
from keras.utils import to_categorical
import environment as env
import seaborn as sns
import matplotlib.pyplot as plt
from scenarios import generate_scenario, ScenarioType

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


def text_to_screen(screen, text, x, y, size=30,
                   color=(24, 45, 62), font_type='Helvetica'):
    text = str(text)
    font = pygame.font.SysFont(font_type, size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))


def plot_stats(array_counter, array_score):
    sns.set(color_codes=True)
    ax = sns.regplot(np.array([array_counter])[0], np.array([array_score])[0], color="b", x_jitter=.1,
                     line_kws={'color': 'green'})
    ax.set(xlabel='games', ylabel='score')
    plt.show()


pygame.init()
agent = DQNAgent()
score_plot = []
counter_plot = []


def run_game():
    display_width = 700
    display_height = 600

    reward = 0

    env_speed = 1
    env_dim = [display_width, display_height]
    environment = generate_scenario(env_speed, env_dim, ScenarioType.LONG_LASTING)

    size = [display_width, display_height]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Ferrytale")

    boat_list = pygame.sprite.OrderedUpdates()
    all_sprites_list = pygame.sprite.Group()
    all_sprites_list.add(environment.state.top_shore)
    all_sprites_list.add(environment.state.bottom_shore)
    all_sprites_list.add(environment.state.goal)
    all_sprites_list.add(environment.state.agent)
    
    boat_list.add(environment.state.boats)
    all_sprites_list.add(environment.state.boats)

    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Hide the mouse cursor
    pygame.mouse.set_visible(0)


    # -------- Main Program Loop -----------
    while not done:
        # Get the current state
        state_old = agent.get_state(environment.state)

        # Perform a random action based on agent.epsilon, or choose the action
        if randint(0, 100) < agent.epsilon:
            final_move = to_categorical(randint(0, 8), num_classes=9)
            final_move = environment.index_to_action(np.nonzero(final_move)[0][0])
            # print("RANDOM")
        else:
            # Predict action based on the current state
            prediction = agent.model.predict(state_old.reshape(1, 49))
            print("state_old:", state_old)
            # print("prediction[0]:", prediction[0])
            final_move = to_categorical(np.argmax(prediction[0]), num_classes=9)
            # print("final move:", final_move)
            final_move = environment.index_to_action(np.nonzero(final_move)[0][0])
            # print("CHOSEN")

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

        # Perform new move and get new reward
        next_state, reward, env_done = environment.step(final_move)

        # Get new state
        state_new = agent.get_state(next_state)

        # Train short memory based on new action and state
        agent.train_short_memory(state_old, final_move, reward, state_new, env_done)

        # Store new data into long term memory
        agent.remember(state_old, final_move, reward, state_new, env_done)

        if env_done or reward < -2000:
            done = True

        text_to_screen(screen, "Reward {0}".format(round(reward)), display_width - 160, display_height - 50)
        pygame.display.flip()

        # Limit frames per second
        clock.tick(1000)

    agent.replay_new(agent.memory)
    agent.game_counter += 1
    print("Game", agent.game_counter, "             Score:", reward)
    score_plot.append(reward)
    counter_plot.append(agent.game_counter)
    return True


restart = True
while restart:
    restart = run_game()
    if agent.game_counter == 80:
        restart = False

agent.model.save_weights("weights.hdf5")
plot_stats(counter_plot, score_plot)

# Close the window and quit.
pygame.quit()
