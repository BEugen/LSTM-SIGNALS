import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


def main():
    df = pd.read_csv('railsdataset_comp.csv', sep=';')
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(20, 10))
    df.plot(y='p', ax=ax1, color='red', label='p')
    df.plot(y='t', ax=ax1, color='blue', label='t')
    df['sqr'] = (df['p'].apply(lambda x: x*x) - df['t'].apply(lambda x: x*x)).\
        apply(lambda x: math.fabs(x)).apply(lambda x: math.sqrt(x))
    df.plot(y='sqr', ax=ax2, color='red', label='sq')
    df = windsmotch(df, 'sqr')
    df.plot(y='sqr', ax=ax3, color='red', label='sq')
    plt.show()


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

if __name__ == '__main__':
    main()

