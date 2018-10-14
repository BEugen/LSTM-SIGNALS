import os
from datetime import timedelta, datetime
import pandas as pd


ch_null = {'1': 142, '2': 104, '3': 123, '4': 146}

def main():
    pd_bed = pd.read_csv('/mnt/data/data/LSTM-RL/rs/ep/bax/2018_08_24 14_22_31.csv', sep=';', parse_dates=[1])
    df = windsmotch(pd_bed, ['p1_ch1', 'p1_ch2', 'p1_ch3', 'p1_ch4'])
    for i in range(1, 5):
        df['p1_ch' + str(i)] = df['p1_ch' + str(i)] - ch_null[str(i)]
    print(df)

def windsmotch(data, column):
    #timedelta(seconds=addtime)
    offset = 0.5
    winsize = 0.15
    stdtimr = data.iloc[0, 1] + timedelta(seconds=winsize)
    endtimr = data.iloc[data.shape[0] - 1, 1]
    rows = []
    columns = ['datetime']
    for x in column:
        columns.append(x)
    while stdtimr <= endtimr:
        row = [stdtimr]
        for i in data[(data['datetime'] > (stdtimr - timedelta(seconds=winsize))) &
                   (data['datetime'] < (stdtimr + timedelta(seconds=winsize)))][columns[1: len(columns)]].max():
            row.append(i)
        rows.append(row)
        stdtimr += timedelta(seconds=offset)
    return pd.DataFrame(rows, columns=columns)


if __name__ == '__main__':
    main()

