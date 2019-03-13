from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten
import keras
import random
import numpy as np
import pandas as pd
import time
import tensorflow as tf
from multiprocessing import cpu_count
#import keras

config = tf.ConfigProto(device_count={'GPU': 0, 'CPU': cpu_count()})
sess = tf.Session(config=config)
keras.backend.set_session(sess)

batch_size = 24
memory_size = 1000
num_of_actions = 9

class DQNAgent(object):
    def __init__(self):
        self.gamma = 0.9
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = 0.01
        self.model = self.network()
        # self.model = self.network("weights.hdf5")  # Use precalculated weights
        self.actual = []
        self.memory = []
        self.game_counter = 0
        self.epsilon = 80 - self.game_counter
        self.loss = 0

    def get_state(self, raw_state):
        state = [0] * 46

        # state[0 - 3]: [player pos x, pos y, vel x, vel y]
        state[0] = raw_state.agent.rect.x
        state[1] = raw_state.agent.rect.y
        state[2] = raw_state.agent.velocity.x
        state[3] = raw_state.agent.velocity.y

        # state[4 - 5]: [dock pos x, pos y, vel x=0, vel y=0]
        state[4] = raw_state.goal.rect.x
        state[5] = raw_state.goal.rect.y

        # state[6 - 46]: [boat pos x, pos y, vel x, vel y], for each boat
        for i in range(len(raw_state.boats)):
            state[6 + 4 * i] = raw_state.boats[i].rect.x
            state[7 + 4 * i] = raw_state.boats[i].rect.y
            state[8 + 4 * i] = raw_state.boats[i].velocity.x
            state[9 + 4 * i] = raw_state.boats[i].velocity.y

        # Normalize the data (values from 0-1)
        state = tf.keras.utils.normalize(np.asarray(state), -1, 2)

        return state[0]

    def network(self, weights=None):
        # crossentropy = keras.losses.categorical_crossentropy
        model = Sequential()
        model.add(Dense(input_dim=46, activation='relu', units=120))  # Current input_dim
        model.add(Dropout(0.15))
        #model.add(Flatten())
        model.add(Dense(120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(9, activation='softmax'))  # Current output_dim
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)  # 'mse'

        if weights:
            model.load_weights(weights)
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory):
        loss = 0
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory

        inputs = np.zeros((batch_size, 46))
        targets = np.zeros((inputs.shape[0], num_of_actions))						  
        #32, 2

        for i in range(len(minibatch)):
            state = minibatch[i][0]
            action = minibatch[i][1]
            reward = minibatch[i][2]
            next_state = minibatch[i][3]
            done = minibatch[i][4]
            #print("action", action, "reward", reward, "next_state", next_state, "done", done)
            start = time.time()
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            
            inputs[i] = state
            targets[i] = self.model.predict(np.array([state]))[0]

            targets[i][np.argmax(action)] = target

            start = time.time()
            #print("Target", target_f)

            #print("Prediction", self.model.predict(np.array([state])))
            #print("Target f", target_f)

        #print("Accuracy:", avg_acc / len(minibatch), "Loss:",avg_loss / len(minibatch))
        loss += self.model.train_on_batch(inputs, targets)
        self.loss += loss
        print("Timestep: %d, Loss: %.2f, Average loss: %.2f" % (self.game_counter, self.loss, self.loss / self.game_counter))


    def train_short_memory(self, state, action, reward, next_state, done):
        target = reward
        #print("target1:", target)
        if not done:
            target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, 46)))[0])
            #print("target2:", target)
        target_f = self.model.predict(state.reshape((1, 46)))
        #print("target_f1:", target_f)
        target_f[0][np.argmax(action)] = target
        #print("target_f2:", target_f)
        self.model.fit(state.reshape((1, 46)), target_f, epochs=1, verbose=0)
