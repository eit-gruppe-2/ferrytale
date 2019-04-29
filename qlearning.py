import keras
import random
import numpy as np
import tensorflow as tf
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from multiprocessing import cpu_count

# Set "'GPU': 0" to 1 or more to run the program on one or more NVIDIA GPUs.
# WARNING: This program is not very well optimized for GPUs and will most likely run slower on a GPU than on a CPU.
config = tf.ConfigProto(device_count={'GPU': 0, 'CPU': cpu_count()})
sess = tf.Session(config=config)
keras.backend.set_session(sess)

# Select the batch size for training.
batch_size = 250


# Class for the agent learning to control the ferry.
class DQNAgent(object):
    def __init__(self):
        self.gamma = 0.9
        self.learning_rate = 0.01
        self.model = self.network()
        # Uncomment the line below to utilize pre-calculated weights instead of generating new ones.
        # self.model = self.network("weights.hdf5")
        self.memory = []
        self.game_counter = 0
        self.epsilon = 80 - self.game_counter
        self.loss = 0

    # Function for turning the raw game state into a format suitable for the neural network.
    @staticmethod
    def get_state(raw_state):
        # Initialize a (1, 46) list of zeros.
        state = [0] * 46

        # state[0 - 3]: [player pos x, pos y, vel x, vel y]
        state[0] = raw_state.agent.rect.x
        state[1] = raw_state.agent.rect.y
        state[2] = raw_state.agent.velocity.x
        state[3] = raw_state.agent.velocity.y

        # state[4 - 5]: [dock pos x, pos y]
        state[4] = raw_state.goal.rect.x
        state[5] = raw_state.goal.rect.y

        # state[6 - 46]: [boat pos x, pos y, vel x, vel y], for each boat. There is space for 10 boats in total.
        for i in range(len(raw_state.boats)):
            state[6 + 4 * i] = raw_state.boats[i].rect.x
            state[7 + 4 * i] = raw_state.boats[i].rect.y
            state[8 + 4 * i] = raw_state.boats[i].velocity.x
            state[9 + 4 * i] = raw_state.boats[i].velocity.y

        # Normalize the data to values between 0 and 1.
        state = tf.keras.utils.normalize(np.asarray(state), -1, 2)

        return state[0]

    # Function for constructing the neural network used in the reinforcement learning.
    def network(self, weights=None):
        model = Sequential()
        model.add(Dense(input_dim=46, activation='relu', units=120))  # Current input_dim
        model.add(Dropout(0.15))
        model.add(Dense(120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(9, activation='softmax'))  # Current output_dim
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)  # 'mse'

        # If choosing to utilize pre-calculated weights, load them.
        if weights:
            model.load_weights(weights)

        return model

    # Function for storing a step in memory.
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    # Function for replaying and learning from games in memory.
    def replay_new(self, memory):
        # Initialize the loss
        loss = 0

        # Select memory to train from.
        if len(memory) > batch_size:
            mini_batch = random.sample(memory, batch_size)
        else:
            mini_batch = memory

        inputs = np.zeros((batch_size, 46))
        targets = np.zeros((inputs.shape[0], 9))

        # Train the agent.
        for i in range(len(mini_batch)):
            state = mini_batch[i][0]
            action = mini_batch[i][1]
            reward = mini_batch[i][2]
            next_state = mini_batch[i][3]
            done = mini_batch[i][4]
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            
            inputs[i] = state
            targets[i] = self.model.predict(np.array([state]))[0]

            targets[i][np.argmax(action)] = target

        # Calculate the loss and print game info.
        loss += self.model.train_on_batch(inputs, targets)
        self.loss += loss

        if self.game_counter % 50 == 0:
            print("Game: %d     Accumulated loss: %.2f      Average loss: %.2f" % (
                self.game_counter, self.loss, self.loss / (self.game_counter + 1)))
