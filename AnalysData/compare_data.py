import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta, datetime


def main():
    pd_bed = pd.read_csv('E:/TMP/rs/bax/2018_08_25 04_42_50.csv', sep=';', parse_dates=[1])
    pd_good = pd.read_csv('E:/TMP/rs/gd/2018_08_30 12_32_49.csv', sep=';', parse_dates=[1])
    stdtimr = pd_bed.iloc[0, 1]
    pd_bed['datetime'] = pd_bed['datetime'] - stdtimr
    stdtimr = pd_good.iloc[0, 1]
    pd_good['datetime'] = pd_good['datetime'] - stdtimr
    pd_bed['diffb'] = pd_bed['p1_ch3'].diff()
    pd_good['diffb'] = pd_good['p1_ch3'].diff()
    pd_avg = wincurve(pd_bed)
    pdg_avg = wincurve(pd_good)
    fig, (ax1, ax3) = plt.subplots(nrows=2, ncols=1)
   # pd_bed.plot(x='datetime', y='p1_ch4', ax=ax1)
   # pd_good.plot(x='datetime', y='p1_ch4', ax=ax1)
    plt.gcf().autofmt_xdate()
    pd_bed.plot(x='datetime', y='diffb', ax=ax1)
    pd_good.plot(x='datetime', y='diffb', ax=ax1)
    pdg_avg.plot(x='datetime', y='diffb', ax=ax3)
    pd_avg.plot(x='datetime', y='diffb', ax=ax3)
    plt.show()


def wincurve(data):
    #timedelta(seconds=addtime)
    offset = 2.0
    winsize = 1.5
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




