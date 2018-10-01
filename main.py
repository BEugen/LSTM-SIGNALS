import  SignalsHeader


def main():
    Sig = SignalsHeader.AsiSignal()
    path = 'test.sig'
    result = Sig.getdata(path)
    return result


if __name__ == '__main__':
    main()

