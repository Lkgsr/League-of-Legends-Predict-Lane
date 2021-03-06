import os
import pickle
import time

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from tensorflow.keras import Model
from tensorflow.keras.layers import Dense, Conv1D, Flatten, Input
from tensorflow_core.python.keras.backend import set_session
from tensorflow_core.python.keras.callbacks import ModelCheckpoint, TensorBoard


class CnnTrain:

    def __init__(self, data_name='data'):
        """
        Setting everything up
        :param data_name: name of the data files
        """
        self.setup()
        # Preparing the model
        self.model = self.prepare_model()
        print('preparing model done')
        # Preparing the data
        self.X, self.y = self.prepare_data(data_name)
        print('preparing data done')

    @staticmethod
    def setup():
        """
        Very use full if you use tensorflow-gpu and your using your GPU at the ame time -> tensorflow want to use the
        whole Video Ram
        :return: None
        """
        config = ConfigProto()
        config.gpu_options.allow_growth = True
        config.log_device_placement = True
        session = InteractiveSession(config=config)
        set_session(session)
        # check if directories for models and logs exists, if not there are created
        if not os.path.isdir("models"):
            os.mkdir("models")
        if not os.path.isdir("logs"):
            os.mkdir("logs")

    @staticmethod
    def prepare_data(name, length=16, save=False, scale=True):
        """
        Load in the data from the given file name and preparing it to a scaled numpy array of numpy array's from 0 to 1
        :param name: name of the data files
        :param length: length of a line from the X data file
        :param save: True to save the prepared data as a pickle file
        :param scale: True for scaling the data between 0 and 1
        :return: numpy array of X and y data
        """
        min_max_scalar = MinMaxScaler()
        with open(f'data/X_{name}.txt', 'r') as x, open(f'data/y_{name}.txt', 'r') as y:
            x_file, y_file = x.readlines(), y.readlines()
        X, y = [], []
        # Making each line from the file a numpy array
        for line_x, line_y in zip(x_file, y_file):
            x_line = line_x.replace('\n', '').split(',')
            # last check if the line of the file has the right length for the array
            if len(x_line) == length:
                X.append(np.array(x_line))
                y_line = line_y.replace('\n', '').split(',')
                y.append(np.array(y_line, dtype=np.int32))
        X, y = np.array(X), np.array(y)
        # Scaling the Data
        if scale:
            X = min_max_scalar.fit_transform(X)
        # May you saved your prepared array with pickle for later
        if save is True:
            with open(f'X_{name}.pickle', 'wb') as x_out_file, open(f'Y_{name}.pickle', 'wb') as y_out_file:
                pickle.dump(X, x_out_file)
                pickle.dump(y, y_out_file)
        print(f'X: {X.shape}, Y: {y.shape}')
        return X, y

    @staticmethod
    def prepare_model():
        """
        Preparing the model
        :return: Keras compiled model
        """
        in_put = Input(shape=(16, 1), name='Input')
        conv1D = Conv1D(153, kernel_size=2, activation='relu', input_shape=(16, 1))(in_put)
        conv1D = Conv1D(153, kernel_size=2, activation='relu', input_shape=(16, 1))(conv1D)
        conv1D = Conv1D(153, kernel_size=2, activation='relu', input_shape=(16, 1))(conv1D)
        conv1D = Conv1D(153, kernel_size=2, activation='relu', input_shape=(16, 1))(conv1D)
        flatten = Flatten()(conv1D)
        dense = Dense(153, activation='softmax')(flatten)
        output = Dense(4, activation='softmax')(dense)
        model = Model(inputs=in_put, outputs=output)
        model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'], )
        return model

    @staticmethod
    def train(model, X, y, name, epochs=100, validation_split=0.3, batch_size=556):
        """
        Train the model
        :param model: compiled Keras model
        :param X: dataset
        :param y: dataset labels
        :param name: name of the model
        :param epochs: how many time you want to go over the data
        :param validation_split: ratio of splitting into train/validation sets
        :param batch_size: How much data get through at once
        :return: None
        """

        # Adding a time stamp to the name so you cant all ways unique names
        name = f"{name}_{int(time.time())}"
        # Setting up Tensorboard Callback to watch the Graph of accuracy and loss
        tensor_board = TensorBoard(log_dir=f'logs\{name}')
        # Setting up ModelCheckpoint the save the model on the best validation accuracy
        checkpoint = ModelCheckpoint(f'models\{name}', monitor='val_accuracy',
                                     mode='max')
        # Train the Model
        model.fit(X, y, validation_split=validation_split, epochs=epochs, batch_size=batch_size,
                  shuffle=True, callbacks=[tensor_board, checkpoint])

    def run(self, name):
        """
        :param name: name of the model
        :return: None
        """
        # Reshaping the data for the conv1D input
        self.X = self.X.reshape(-1, 16, 1)
        # Train the model
        self.train(self.model, self.X, self.y, name + '4_conv1D_153_one_dense_153')
        print('training done')
