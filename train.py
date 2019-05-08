from keras import Sequential
from keras.layers import Dense, Conv1D, Flatten
from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.backend.tensorflow_backend import set_session
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pickle
import time


def setup():
    # Very use full if you use tensorflow-gpu and your using your GPU at the ame time -> tensorflow want to use the
    # whole Video Ram
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
    config.log_device_placement = True      # to log device placement (on which device the operation ran)
                                            # (nothing gets printed in Jupyter, only if you run it standalone)
    sess = tf.Session(config=config)
    set_session(sess)


def prepare_data(name, length=16, save=False, scale=True):
    # Load in the data from the given file name and preparing it to a scaled numpy array of numpy array's from 0 to 1
    min_max_scaler = MinMaxScaler()
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
            y.append(np.array(y_line))
    X, y = np.array(X), np.array(y)
    # Scaling the Data
    if scale:
        X = min_max_scaler.fit_transform(X)
    # May you saved your prepared array with pickle for later
    if save is True:
        with open(f'X_{name}.pickle', 'wb') as x_out_file, open(f'Y_{name}.pickle', 'wb') as y_out_file:
            pickle.dump(X, x_out_file)
            pickle.dump(y, y_out_file)
    print(f'X: {X.shape}, Y: {y.shape}')
    return X, y


def prepare_model():
    # Preparing the model
    model = Sequential()
    model.add(Conv1D(153, kernel_size=2, activation='relu', input_shape=(16, 1)))
    model.add(Conv1D(153, kernel_size=2, activation='relu'))
    model.add(Conv1D(153, kernel_size=2, activation='relu'))
    model.add(Conv1D(153, kernel_size=2, activation='relu'))
    model.add(Flatten())
    model.add(Dense(153, activation='softmax'))
    model.add(Dense(4, activation='softmax'))
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def train(model, X, y, name, epochs=100, validation_split=0.3, batch_size=556):
    # Adding a time stamp to the name so you cant all ways unique names
    name = f"{name}_{int(time.time())}"
    # Setting up Tensorboard Callback to watch the Graph of accuracy and loss
    tensorboard = TensorBoard(log_dir=f'logs/{name}')
    # Setting up ModelCheckpoint the save the model on the best validation accuracy
    checkpoint = ModelCheckpoint(f'models/{name}_{int(time.time())}', monitor='val_acc', verbose=3,
                                 save_best_only=True, mode='max')
    # Train the Model
    model.fit(X, y, validation_split=validation_split, epochs=epochs, batch_size=batch_size,
              callbacks=[tensorboard, checkpoint])


def run(name):
    # Setting everything up
    setup()
    print('setup done')
    # Preparing the data
    x, y = prepare_data('data')
    # Reshaping the data for the conv1D input
    x = x.reshape(-1, 16, 1)
    print('preparing data done')
    # Preparing the model
    model = prepare_model()
    print('preparing model done')
    # Train the model
    train(model, x, y, name + '4_conv1D_153_one_dense_153')
    print('training done')


if __name__ == "__main__":
    run('test')
