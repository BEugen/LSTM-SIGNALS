import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import os

CHANNELS = ['p1_ch1', 'p1_ch2', 'p1_ch3', 'p1_ch4']
def main():
    for channel in CHANNELS:
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(20, 10))
        pd_bed = pd.read_csv('E:/TMP/rs/ep/bax/2018_08_24 14_22_31.csv', sep=';', parse_dates=[1])
        #ax3.set_ylim(-0.1, 200.0)
        for file in os.listdir('E:/TMP/rs/ep/gd/'):
            print(file)
            pd_good = pd.read_csv('E:/TMP/rs/ep/gd/' + file, sep=';', parse_dates=[1])
            stdtimr = pd_good.iloc[0, 1]
            pd_good['datetime'] = pd_good['datetime'] - stdtimr
            pd_good['diffb'] = pd_good[channel].diff() * (-1.0 if 'ch1' in channel or 'ch4' in channel else 1.0)
            pd_avg_g = wincurve(pd_good, channel)
            pd_good.plot(x='datetime', y=channel, ax=ax2, color='blue', legend=None)
            pd_avg_g.plot(x='datetime', y=channel, color='blue', ax=ax3, legend=None)

        stdtimr = pd_bed.iloc[0, 1]
        pd_bed['datetime'] = pd_bed['datetime'] - stdtimr
        pd_bed['diffb'] = pd_bed[channel].diff() * (-1.0 if 'ch1' in channel or 'ch4' in channel else 1.0)
        pd_avg_b = wincurve(pd_bed, channel)
        print(pd_avg_b.shape)
        #pd_avg_g = wincurve(pd_good)
       # pd_bed.plot(x='datetime', y='p1_ch4', ax=ax1)
       # pd_good.plot(x='datetime', y='p1_ch4', ax=ax1)
        pd_bed.plot(x='datetime', y=channel, ax=ax2, color='red', label='bad ch (' + channel + ')')
        #pd_good.plot(x='datetime', y=CHANNEL, ax=ax2, color='green', label='good ch')
        pd_bed.plot(x='datetime', y='diffb', ax=ax1, color='red', label='bad dy/dx (' + channel + ')')
        #pd_good.plot(x='datetime', y='diffb', ax=ax1, color='green', label='good dy/dx')
        pd_avg_b.plot(x='datetime', y=channel, ax=ax3, color='red', label='bad ac dy/dx (' + channel + ')')
        #pd_avg_g.plot(x='datetime', y='diffb', ax=ax3, color='green', label='good ac dy/dx')
        plt.show()


def wincurve(data, column):
    #timedelta(seconds=addtime)
    offset = 0.5
    winsize = 0.15
    stdtimr = data.iloc[0, 1] + timedelta(seconds=winsize)
    endtimr = data.iloc[data.shape[0] - 1, 1]
    rows = []
    columns = ['datetime', column]
    while stdtimr <= endtimr:
        rows.append([stdtimr, data[(data['datetime'] > (stdtimr - timedelta(seconds=winsize))) &
                   (data['datetime'] < (stdtimr + timedelta(seconds=winsize)))][column].max()])
        stdtimr += timedelta(seconds=offset)
    return pd.DataFrame(rows, columns=columns)


if __name__ == '__main__':
    main()




