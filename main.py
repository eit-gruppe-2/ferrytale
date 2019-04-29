import pygame
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from qlearning import DQNAgent
from random import randint
from keras.utils import to_categorical
from scenarios import generate_scenario, ScenarioType

# Define the background colour.
BLUE = (0, 128, 180)

# Initialize pygame, the machine learning agent and lists for plotting the scores to the games.
pygame.init()
agent = DQNAgent()
score_plot = []
counter_plot = []

# Select the desired number of games for the agent to run and learn from.
number_of_games = 5000

# Select whether to display the game screen or not and control the game's frame rate.
display_screen = False
FPS = 60


# Class describing the ferry.
class Ferry(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()


# Function for displaying text on the game screen.
def text_to_screen(screen, text, x, y, size=30,
                   color=(24, 45, 62), font_type='Helvetica'):
    text = str(text)
    font = pygame.font.SysFont(font_type, size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))


# Function for plotting the scores to the games.
def plot_stats(array_counter, array_score):
    sns.set(color_codes=True)
    ax = sns.regplot(np.array([array_counter])[0], np.array([array_score])[0], color="b", x_jitter=.1,
                     line_kws={'color': 'green'})
    ax.set(xlabel='games', ylabel='score')
    plt.show()


# Main function for running the game.
def run_game(display_game):
    # Set the display resolution.
    display_width = 700
    display_height = 600

    # Initialize the reward and accumulated reward.
    reward = 0
    reward_acc = 0

    # Initialize the environment.
    env_speed = 10
    size = [display_width, display_height]
    environment = generate_scenario(env_speed, size, ScenarioType.COMPLEX)
    environment.given_rewards = []

    # If choosing to display the game screen, initialize the sprites and screen for drawing.
    if display_game:
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Ferrytale")

        # Add boats.
        boat_list = pygame.sprite.OrderedUpdates()
        boat_list.add(environment.state.boats)

        # Add shores, dock, ferry and boats.
        all_sprites_list = pygame.sprite.Group()
        all_sprites_list.add(environment.state.top_shore)
        all_sprites_list.add(environment.state.bottom_shore)
        all_sprites_list.add(environment.state.goal)
        all_sprites_list.add(environment.state.agent)
        all_sprites_list.add(environment.state.boats)

        # Used in managing the game's frame rate.
        clock = pygame.time.Clock()

    done = False
    # -------- Main Program Loop -----------
    while not done:
        # Get the current state.
        state_old = agent.get_state(environment.state)

        # Perform a random action based on agent.epsilon, or choose the action.
        if randint(0, 100) < agent.epsilon:
            final_move = to_categorical(randint(0, 8), num_classes=9)
            final_move_environment = environment.index_to_action(np.nonzero(final_move)[0][0])
        else:
            # Predict an action based on the current state.
            prediction = agent.model.predict(state_old.reshape(1, 46))
            final_move = to_categorical(np.argmax(prediction[0]), num_classes=9)
            final_move_environment = environment.index_to_action(np.nonzero(final_move)[0][0])

        # If choosing to display the game screen, draw the sprites and the score.
        if display_game:
            screen.fill(BLUE)
            all_sprites_list.draw(screen)
            text_to_screen(screen, "Reward {0}".format(round(reward)), display_width - 160, display_height - 50)
            pygame.display.flip()
            clock.tick(FPS)

        # Perform the selected action and get the new reward.
        next_state, reward, env_done = environment.step(final_move_environment)
        reward_acc += reward

        # Get the new state.
        state_new = agent.get_state(next_state)

        # Remember the previous state, action, resulting reward, new state and whether the game finished or not.
        agent.remember(state_old, final_move, reward, state_new, env_done)

        # Exit the current game if it is finished.
        if env_done:
            done = True

    # Learn from the recent game.
    agent.replay_new(agent.memory)
    agent.game_counter += 1
    score_plot.append(reward_acc)
    counter_plot.append(agent.game_counter)

    return True


# Loop for running the game the desired amount of times.
restart = True
while restart:
    restart = run_game(display_screen)
    if agent.game_counter == number_of_games:
        restart = False

# Save the trained weights for reuse if desired.
agent.model.save_weights("weights.hdf5")

# Plot the scores to the games.
plot_stats(counter_plot, score_plot)

# Close the window and quit the game.
pygame.quit()
