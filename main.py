import  SignalsHeader


def main():
    SigHeader = SignalsHeader.SignalHeader()
    path = 'test.sig'
    result = SigHeader.ParseHeader(path)
    return result


if __name__ == '__main__':
    main()

