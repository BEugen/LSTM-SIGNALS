import SignalsHeader
import matplotlib.pyplot as plt
import json
import os

labelsd = { 0: 'normal', 1: 'badspeed', 2: 'badshaft'}
FILEFOLDER = 'fcsv'
FILEDESC = 'fjsn'

def writelabelsdata(filename, labels):
    lc = LabelsLSTM()
    lc.filename = filename
    lc.labels = labels
    lc.labeldesc = labelsd[labels]
    with open(FILEDESC + '/' + filename + '.json', 'w') as fj:
        json.dump(lc.__dict__, fj)




def main():
    if not os.path.exists(FILEFOLDER):
        os.makedirs(FILEFOLDER)
    if not os.path.exists(FILEDESC):
        os.makedirs(FILEDESC)
    Sig = SignalsHeader.AsiSignal()
    path = '2017_08_22 22_11_12.sig'
    result = Sig.getdata(path)
    filename = os.path.splitext(path)[0]
    result.to_csv(FILEFOLDER + '/' + filename + '.csv', sep=';')
    writelabelsdata(filename, 0)
    #result['avg'] = result.mean(axis=1)
    #result['diff'] = result['p1_ch2'].diff()
    #ax = plt.gca()
    #result.plot(x='datetime', y='avg', ax=ax)
    #result.plot(x='datetime', y='diff', ax=ax)
    #result.plot(x='datetime', y='p1_ch3', ax=ax)
    #result.plot(x='datetime', y='p1_ch4', ax=ax)
    #plt.show()
    return result


class LabelsLSTM:
    def __init__(self):
        self.filename = ''
        self.labels = 0
        self.labeldesc = ''



if __name__ == '__main__':
    main()

