import os
from datetime import timedelta, datetime
import pandas as pd
import json

column = ['p1_ch1', 'p1_ch2', 'p1_ch3', 'p1_ch4']
ch_null = {'1': 142, '2': 104, '3': 123, '4': 146}
PATH_JSON = '/mnt/data/data/LSTM-RL/rs/jsn/'
PATH_FILE = '/mnt/data/data/LSTM-RL/rs/ep/gd/'#'E:/TMP/rs/ep/gd/'

def main():
    dataset = pd.DataFrame([], columns=column)
    for file in os.listdir(PATH_FILE):
        pd_bed = pd.read_csv(PATH_FILE + file, sep=';', parse_dates=[1])
        df = windsmotch(pd_bed, column)
        ch_null = getnullforchannels(PATH_JSON + os.path.splitext(file)[0] + '.json')
        for i in range(1, 5):
            df['p1_ch' + str(i)] = df['p1_ch' + str(i)] - ch_null[str(i)]
        ind = df[df[column] > 50.0].sort_index(ascending=0).first_valid_index()
        df.drop('datetime', axis=1)
        print(file, df[column].max())
        dataset = dataset.append(df[0: ind+10].drop('datetime', axis=1))
    dataset.to_csv('railsdataset.csv', sep=';', index=False)


def windsmotch(data, col):
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

