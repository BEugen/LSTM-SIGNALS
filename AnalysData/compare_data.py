import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta, datetime


def main():
    pd_bed = pd.read_csv('/mnt/data/data/LSTM-RL/rs/ep/bax/2018_08_24 14_22_31.csv', sep=';', parse_dates=[1])
    pd_good = pd.read_csv('/mnt/data/data/LSTM-RL/rs/ep/gd/2018_09_22 07_38_43.csv', sep=';', parse_dates=[1])
    stdtimr = pd_bed.iloc[0, 1]
    pd_bed['datetime'] = pd_bed['datetime'] - stdtimr
    stdtimr = pd_good.iloc[0, 1]
    pd_good['datetime'] = pd_good['datetime'] - stdtimr
    pd_bed['diffb'] = pd_bed['p1_ch3'].diff()
    pd_good['diffb'] = pd_good['p1_ch3'].diff()
    pd_avg_b = wincurve(pd_bed)
    print(pd_avg_b.shape)
    pd_avg_g = wincurve(pd_good)
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(20, 10))
   # pd_bed.plot(x='datetime', y='p1_ch4', ax=ax1)
   # pd_good.plot(x='datetime', y='p1_ch4', ax=ax1)
    pd_bed.plot(x='datetime', y='p1_ch3', ax=ax2, color='red', label='bad ch')
    pd_good.plot(x='datetime', y='p1_ch3', ax=ax2, color='green', label='good ch')
    pd_bed.plot(x='datetime', y='diffb', ax=ax1, color='red', label='bad dy/dx')
    pd_good.plot(x='datetime', y='diffb', ax=ax1, color='green', label='good dy/dx')
    pd_avg_b.plot(x='datetime', y='diffb', ax=ax3, color='red', label='bad ac dy/dx')
    pd_avg_g.plot(x='datetime', y='diffb', ax=ax3, color='green', label='good ac dy/dx')
    plt.show()


def wincurve(data):
    #timedelta(seconds=addtime)
    offset = 2.0
    winsize = 1.0
    stdtimr = data.iloc[0, 1] + timedelta(seconds=winsize)
    endtimr = data.iloc[data.shape[0] - 1, 1]
    rows = []
    columns = ['datetime', 'diffb']
    while stdtimr <= endtimr:
        rows.append([stdtimr, data[(data['datetime'] > (stdtimr - timedelta(seconds=winsize))) &
                   (data['datetime'] < (stdtimr + timedelta(seconds=winsize)))]['diffb'].max()])
        stdtimr += timedelta(seconds=offset)
    return pd.DataFrame(rows, columns=columns)


if __name__ == '__main__':
    main()




