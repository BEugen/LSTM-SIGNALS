import SignalsHeader
import os
import json

FILEDESC = '/home/eugen/Загрузки/Result'
FILESIG = '/home/eugen/Загрузки/Sig_22.10.18/'

def writelabelsdata(filename, labels, platforms):
    lc = LabelsLSTM()
    lc.filename = filename
    lc.badspeed = labels[0]
    lc.badaxle = labels[1]
    lc.scnumber = labels[2]
    lc.full = labels[3]
    lc.minspeed = labels[4]
    lc.maxspeed = labels[5]
    lc.axles = labels[6]
    lc.weights = labels[7]
    for r in platforms:
        lc.platforms.append(r.__dict__)
    with open(FILEDESC + '/' + filename + '.json', 'w') as fj:
        json.dump(lc.__dict__, fj)


class LabelsLSTM:
    def __init__(self):
        self.filename = ''
        self.badspeed = False
        self.badaxle = False
        self.labeldesc = ''
        self.scnumber = 0
        self.full = False
        self.minspeed = 0
        self.maxspeed = 0
        self.platforms = []
        self.axles = []
        self.weights = []


def main():
    for sfile in os.listdir(FILESIG):
        filename = os.path.splitext(sfile)[0]
        Sig = SignalsHeader.AsiSignal()
        result, platforms = Sig.getdata(FILESIG + sfile)
        result.to_csv(FILEDESC + '/' + filename + '.csv', sep=';')
        writelabelsdata(filename, [False, True, 301, False, 3.0, 6.0, [], []], platforms)


if __name__ == '__main__':
    main()
