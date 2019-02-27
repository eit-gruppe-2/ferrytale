from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
import random
import numpy as np
import pandas as pd


class DQNAgent(object):
    def __init__(self):
        self.gamma = 0.9
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = 0.0005
        self.model = self.network()
        # self.model = self.network("weights.hdf5")  # Use precalculated weights
        self.actual = []
        self.memory = []
        self.game_counter = 0
        self.epsilon = 80 - self.game_counter

    def get_state(self, raw_state):
        state = [[0] * 4] * 21

        # state[0]: [player pos x, pos y, vel x, vel y]
        state[0] = [raw_state.agent.rect.x, raw_state.agent.rect.y,
                    raw_state.agent.velocity.x, raw_state.agent.velocity.y]

        # state[1]: [dock pos x, pos y, vel x=0, vel y=0]
        state[1] = [raw_state.goal.rect.x, raw_state.goal.rect.y, 0, 0]

        # state[2-16]: [boat pos x, pos y, vel x, vel y], for each boat
        for i in range(len(raw_state.boats)):
            state[2 + i] = [raw_state.boats[i].rect.x, raw_state.boats[i].rect.y,
                            raw_state.boats[i].velocity.x, raw_state.boats[i].velocity.y]

        return np.asarray(state)

    def network(self, weights=None):
        model = Sequential()
        model.add(Dense(output_dim=120, activation='relu', input_shape=(21, 4)))  # Current input_dim
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=9, activation='softmax'))  # Current output_dim
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if weights:
            model.load_weights(weights)
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory):
        if len(memory) > 1000:
            minibatch = random.sample(memory, 1000)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            target_f = self.model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

    def train_short_memory(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, 21, 4)))[0])
        target_f = self.model.predict(state.reshape((1, 21, 4)))
        target_f[0][np.argmax(action)] = target
        self.model.fit(state.reshape((1, 21, 4)), target_f, epochs=1, verbose=0)