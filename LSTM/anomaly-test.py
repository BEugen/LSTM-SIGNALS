import pandas as pd
import matplotlib.pyplot as plt
import math
from keras.models import Sequential
from keras.optimizers import SGD, Adam, RMSprop
from keras.layers import LSTM, Dense, Dropout, Activation
from sklearn.preprocessing import MinMaxScaler
from keras.models import model_from_json
import numpy as np
from datetime import timedelta, datetime
import os
import json

CHANNEL = 4
LOOP_BACK = 64
OPTIM = Adam(lr=0.001)

column = ['p1_ch1', 'p1_ch2', 'p1_ch3', 'p1_ch4']
ch_null = {'1': 142, '2': 104, '3': 123, '4': 146}
PATH_JSON = '/mnt/data/data/LSTM-RL/rs/jsn/'
PATH_FILE = '/mnt/data/data/LSTM-RL/rs/ep/bax/'#'E:/TMP/rs/ep/gd/'


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

def main():
    for file in os.listdir(PATH_FILE):
        if CHANNEL == 2 or CHANNEL == 3:
            nn_name = 'lstmbi-rl-23'
        else:
            nn_name = 'lstmbi-rl-14'

        df = pd.DataFrame([], columns=column)
        pd_bed = pd.read_csv(PATH_FILE + file, sep=';', parse_dates=[1])
        df = windsmotcha(pd_bed, column)
        ch_null = getnullforchannels(PATH_JSON + os.path.splitext(file)[0] + '.json')
        for i in range(1, 5):
            df['p1_ch' + str(i)] = df['p1_ch' + str(i)] - ch_null[str(i)]
        ind = df[df[column] > 50.0].sort_index(ascending=0).first_valid_index()
        df.drop('datetime', axis=1)
        print(file, df[column].max())
        df = df.append(df[0: ind+10].drop('datetime', axis=1))
        #dataset.to_csv('railsdataset_bad.csv', sep=';', index=False)

        #df = pd.read_csv('railsdataset_bad.csv', sep=';')
        data = df['p1_ch' + str(CHANNEL)].tolist()
        data = np.array(data).astype('float32').reshape(-1, 1)
        print(data.shape)
        scaler = MinMaxScaler(feature_range=(0, 1))
        data = scaler.fit_transform(data)
        X_train_b, X_test_b, Y_train_b, Y_test_b = load_data(data, LOOP_BACK)
        X_train_b = np.reshape(X_train_b, (X_train_b.shape[0], 1, X_train_b.shape[1]))

        json_file = open(nn_name + '.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights(nn_name + '.h5')
        model.compile(loss='mae', optimizer=OPTIM)


        yhat = model.predict(X_train_b)
        yhat_inverse = scaler.inverse_transform(yhat.reshape(-1, 1))
        testY_inverse = scaler.inverse_transform(Y_train_b.reshape(-1, 1))
        #yhat_inverse = np.roll(yhat_inverse, -1)
        a = np.concatenate([yhat_inverse, testY_inverse], axis=1)
        df = pd.DataFrame(a, columns=['p', 't'])
        ds = widows_distance(yhat_inverse, testY_inverse)

        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(30, 20))
        df.plot(y='p', ax=ax1, color='red', label='p')
        df.plot(y='t', ax=ax1, color='blue', label='t')
        df['sqr'] = (df['p'].apply(lambda x: x*x) - df['t'].apply(lambda x: x*x)).\
            apply(lambda x: math.fabs(x)).apply(lambda x: math.sqrt(x))
        df.plot(y='sqr', ax=ax2, color='red', label='sq')
        df = windsmotch(df, 'sqr')
        df.plot(y='sqr', ax=ax3, color='red', label='sq')
        #plt.show()
        plt.plot(ds, label='predict')
        fig.savefig(os.path.splitext(file)[0] + '.pdf')


def widows_distance(p, t):
    offset = 16
    winsize = 8
    res = np.zeros(p.shape)
    for i in range(winsize, p.shape[0]-1, offset):
        sq = np.sqrt(np.abs(np.subtract(np.power(p[i-winsize: i+winsize], 2),
                                        np.power(t[i-winsize: i+winsize], 2)))).min()
        res[i-winsize: i+winsize] = sq
    return res


def windsmotch(data, col):
    offset = 10
    winsize = 5
    for i in range(winsize, data.shape[0] - winsize, offset):
        data.loc[i-winsize: i+winsize, col] = avgr(data.loc[i-winsize: i+winsize, col])
    return data


def avgr(data):
    max = data.max()
    min = data.min()
    t = np.mean(data[(data < (max-max*0.3)) & (data > (min+min*0.3))])
    return t


def windsmotcha(data, col):
    offset = 0.2
    winsize = 0.1
    stdtimr = data.iloc[0, 1] + timedelta(seconds=winsize)
    endtimr = data.iloc[data.shape[0] - 1, 1]
    rows = []
    columns = ['datetime']
    for x in col:
        columns.append(x)
    while stdtimr <= endtimr:
        row = [stdtimr]
        for i in data[(data['datetime'] > (stdtimr - timedelta(seconds=winsize))) &
                   (data['datetime'] < (stdtimr + timedelta(seconds=winsize)))][columns[1: len(columns)]].max():
            row.append(i)
        rows.append(row)
        stdtimr += timedelta(seconds=offset)
    df = pd.DataFrame(rows, columns=columns)
    return df


def getnullforchannels(file):
    f = open(file)
    data = json.load(f)
    f.close()
    chnull = {}
    p = data['platforms'][0]
    chnull['1'] = p['Canal1NullCode']
    chnull['2'] = p['Canal2NullCode']
    chnull['3'] = p['Canal3NullCode']
    chnull['4'] = p['Canal4NullCode']
    return chnull


if __name__ == '__main__':
    main()






