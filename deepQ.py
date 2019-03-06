from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten
import keras
import random
import numpy as np
import pandas as pd
import time

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
        state = [0] * 49

        # state[0 - 3]: [player pos x, pos y, vel x, vel y]
        state[0] = raw_state.agent.rect.x
        state[1] = raw_state.agent.rect.y
        state[2] = raw_state.agent.velocity.x
        state[3] = raw_state.agent.velocity.y

        # state[4 - 5]: [dock pos x, pos y, vel x=0, vel y=0]
        state[4] = raw_state.goal.rect.x
        state[5] = raw_state.goal.rect.y

        # state[6 - 49]: [boat pos x, pos y, vel x, vel y], for each boat
        for i in range(len(raw_state.boats)):
            state[6 + 4 * i] = raw_state.boats[i].rect.x
            state[7 + 4 * i] = raw_state.boats[i].rect.y
            state[8 + 4 * i] = raw_state.boats[i].velocity.x
            state[9 + 4 * i] = raw_state.boats[i].velocity.y

        return np.asarray(state)

    def network(self, weights=None):
        crossentropy = keras.losses.categorical_crossentropy
        model = Sequential()
        model.add(Dense(input_dim=49, activation='relu', units=120))  # Current input_dim
        model.add(Dropout(0.15))
        # model.add(Flatten())
        model.add(Dense(units=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(units=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(units=9, activation='softmax'))  # Current output_dim
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt, metrics=['accuracy'])  # 'mse'

        if weights:
            print("HEEEEEEEEEEEEEEEYYYYYYYYYYYYYY")
            model.load_weights(weights)
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory):
        if len(memory) > 1000:
            minibatch = random.sample(memory, 1000)
        else:
            minibatch = memory

        avg_acc = 0
        avg_loss = 0
        

        for state, action, reward, next_state, done in minibatch:
            #print("action", action, "reward", reward, "next_state", next_state, "done", done)
            start = time.time()
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            #print("Target reward", target, reward, self.model.predict(np.array([next_state])))
            target_f = self.model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            start = time.time()

            history = self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

            avg_acc += history.history["acc"][0]
            avg_loss += history.history["loss"][0]

        print("Accuracy:", avg_acc / len(minibatch), "Loss:",avg_loss / len(minibatch), "Dur", str(time.time() - start) + "ms")

    def train_short_memory(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, 49)))[0])
        target_f = self.model.predict(state.reshape((1, 49)))
        target_f[0][np.argmax(action)] = target
        self.model.fit(state.reshape((1, 49)), target_f, epochs=1, verbose=0)
