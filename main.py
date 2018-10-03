import SignalsHeader
import matplotlib.pyplot as plt


def main():
    Sig = SignalsHeader.AsiSignal()
    path = '2018_07_06 11_05_39.sig'
    result = Sig.getdata(path)
    ax = plt.gca()
    result.plot(x='datetime', y='p1_ch1', ax=ax)
    result.plot(x='datetime', y='p1_ch2', ax=ax)
    result.plot(x='datetime', y='p1_ch3', ax=ax)
    result.plot(x='datetime', y='p1_ch4', ax=ax)
    plt.show()
    return result


if __name__ == '__main__':
    main()

