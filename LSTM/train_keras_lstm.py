from keras.utils import np_utils
from keras.models import Sequential
from keras.optimizers import SGD, Adam, RMSprop
from keras.layers import LSTM, Dense, Dropout, Activation
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.metrics import mean_squared_error
from math import sqrt
import os
from keras.callbacks import TensorBoard
from time import time
import pandas as pd
from matplotlib import pyplot

CHANNEL = 1
LOOP_BACK = 100
BATCH_SIZE = 100
NB_EPOCH = 600
VERBOSE = 1
OPTIM = RMSprop()#Adam(lr=INIT_LR, decay=INIT_LR / NB_EPOCH)
LENGHT = 10


def load_data(data, loop_back=1):
    split_size = int(data.shape[0] * 0.8)
    train = data[0:split_size, :]
    test = data[split_size:, :]
    trainX, trainY = create_dataset(train, loop_back)
    testX, testY = create_dataset(test, loop_back)
    return trainX, testX, trainY, testY


def create_dataset(dataset, loopback=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - loopback):
        dataX.append(dataset[i:(i+loopback), 0])
        dataY.append(dataset[i+loopback, 0])
    return np.array(dataX), np.array(dataY)


def lstm(shape):
    model = Sequential()
    model.add(LSTM(100, input_shape=shape))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    return model


def main():
    df = pd.read_csv('railsdataset.csv', sep=';')
    data = df['p1_ch' + str(CHANNEL)].tolist()
    data = np.array(data).astype('float32').reshape(-1, 1)
    print(data.shape)
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(data)
    X_train, X_test, Y_train, Y_test = load_data(data, LOOP_BACK)
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))
    #tensorboard = TensorBoard(log_dir="logs/{}".format(time()), write_graph=True, write_grads=True, write_images=True,
    #                          histogram_freq=0)
    # fit
    model = lstm((X_train.shape[1], X_train.shape[2]))
    model.compile(loss='mae', optimizer=OPTIM)
    history = model.fit(X_train, Y_train, batch_size=BATCH_SIZE, epochs=NB_EPOCH, verbose=VERBOSE,
                        validation_data=(X_test, Y_test),
                        shuffle=False) #callbacks=[tensorboard]
    pyplot.plot(history.history['loss'], label='train')
    pyplot.plot(history.history['val_loss'], label='test')
    pyplot.legend()
    pyplot.show()

    yhat = model.predict(X_test)
    pyplot.plot(yhat, label='predict')
    pyplot.plot(Y_test, label='true')
    pyplot.legend()
    pyplot.show()

    yhat_inverse = scaler.inverse_transform(yhat.reshape(-1, 1))
    testY_inverse = scaler.inverse_transform(Y_test.reshape(-1, 1))
    rmse = sqrt(mean_squared_error(testY_inverse, yhat_inverse))
    print('Test RMSE: %.3f' % rmse)
    #yhat_inverse = np.roll(yhat_inverse, -1)
    pyplot.plot(yhat_inverse[200:300], label='predict')
    pyplot.plot(testY_inverse[200:300], label='actual', alpha=0.5)
    pyplot.legend()
    pyplot.show(figsize=(20, 10))

    df = pd.read_csv('railsdataset_bad.csv', sep=';')
    data = df['p1_ch' + str(CHANNEL)].tolist()
    data = np.array(data).astype('float32').reshape(-1, 1)
    print(data.shape)
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(data)
    X_train_b, X_test_b, Y_train_b, Y_test_b = load_data(data, LOOP_BACK)
    X_train_b = np.reshape(X_train_b, (X_train_b.shape[0], 1, X_train_b.shape[1]))
    yhat = model.predict(X_train_b)
    yhat_inverse = scaler.inverse_transform(yhat.reshape(-1, 1))
    testY_inverse = scaler.inverse_transform(Y_train_b.reshape(-1, 1))
    #yhat_inverse = np.roll(yhat_inverse, -1*LOOP_BACK)
    yha_diff = np.diff(yhat_inverse.reshape(1, -1)).reshape(-1, 1)
    testY_diff = np.diff(testY_inverse.reshape(1, -1)).reshape(-1, 1)
    for i in range(len(yha_diff)):
        yha_diff[i] = 1.0 if yha_diff[i] >= 0 else -1.0
        testY_diff[i] = 1.0 if testY_diff[i] >= 0 else -1.0
    sq = np.multiply(yha_diff, testY_diff)
    pyplot.plot(yhat_inverse, label='predict')
    pyplot.plot(testY_inverse, label='actual', alpha=0.5)
    #pyplot.plot(sq[500:1200], label='sq')
    pyplot.legend()
    pyplot.show(figsize=(20, 10))
    pyplot.plot(sq[0:300], label='sq')
    pyplot.legend()
    pyplot.show(figsize=(20, 10))


if __name__ == '__main__':
    main()
