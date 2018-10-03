import SignalsHeader
import matplotlib.pyplot as plt


def main():
    Sig = SignalsHeader.AsiSignal()
    path = '2017_08_22 22_11_12.sig'
    result = Sig.getdata(path)
    result['avg'] = result.mean(axis=1)
    result['diff'] = result['p1_ch2'].diff()
    ax = plt.gca()
    #result.plot(x='datetime', y='avg', ax=ax)
    result.plot(x='datetime', y='diff', ax=ax)
    #result.plot(x='datetime', y='p1_ch3', ax=ax)
    #result.plot(x='datetime', y='p1_ch4', ax=ax)
    plt.show()
    return result


if __name__ == '__main__':
    main()

