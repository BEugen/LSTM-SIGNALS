import SignalsHeader
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import pyodbc
import fnmatch


MIN_SPEED = 4
MAX_SPEED = 6
DELTASPEED = 3
MAX_AXLE = 6
FILEFOLDER = 'Y:/Backup/CHCSV/fcsv'
FILEDESC = 'Y:/Backup/CHCSV/fjsn'
START_ID = 2254
END_ID = 2 #1195

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


def getsqldata(id):
    labels = []
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=172.31.182.30;DATABASE=RailScales;UID=pd;PWD=yjdfzPtkfylbz456*')
    dfr = pd.read_sql('select DTWeighting as dtb, scaleid, speed, axlecount, ordernumber, weight from '
                      '[RailScales].[dbo].[Weighings] where NumberWeighing = {}'
                      ' order by ordernumber'.format(id),
                      conn)
    dt = dfr['dtb'].fillna(-1).apply(pd.to_datetime).min()
    fileforsearch = filename(dt)
    maxspeed = dfr['speed'].abs().max()
    minspeed = dfr['speed'].abs().min()
    if maxspeed > MAX_SPEED or minspeed < MIN_SPEED or (maxspeed - minspeed) > DELTASPEED:
        labels.append(True)
    else:
        labels.append(False)
    if dfr['axlecount'].max() > MAX_AXLE:
        labels.append(True)
    else:
        labels.append(False)
    if dfr['scaleid'][0] == 1:
        labels.append(301)
    else:
        labels.append(303)
    if dfr['weight'].max() > 130.0:
        labels.append(True)
    else:
        labels.append(False)
    labels.append(minspeed)
    labels.append(maxspeed)
    ax = []
    for x in dfr['axlecount']:
        ax.append(x)
    labels.append(ax)
    ax = []
    for x in dfr['weight']:
        ax.append(x)
    labels.append(ax)
    return fileforsearch, labels


def filename(dt):
    return str(dt.year) + '_' + \
          ('0' + str(dt.month) if dt.month < 10 else str(dt.month)) + '_' + \
          ('0' + str(dt.day) if dt.day < 10 else str(dt.day)) + ' ' + \
          ('0' + str(dt.hour) if dt.hour < 10 else str(dt.hour)) + '_' + \
          ('0' if dt.minute < 10 else str(int(dt.minute/10)))


def main():
    if not os.path.exists(FILEFOLDER):
        os.makedirs(FILEFOLDER)
    if not os.path.exists(FILEDESC):
        os.makedirs(FILEDESC)
    id = START_ID
    while id > END_ID:
        sfile, labels = getsqldata(id)
        path = 'Y:/Backup/' + str(labels[2]) + '/CH/'
        for file in os.listdir(path):
            if fnmatch.fnmatch(file, sfile + '*'):
                sfile = file
                break
        print(id, sfile)
        if not 'sig' in sfile:
            id -= 1
            continue
        Sig = SignalsHeader.AsiSignal()
        result, platforms = Sig.getdata(path + sfile)
        if result is None:
            id -= 1
            continue
        filename = os.path.splitext(sfile)[0]
        result.to_csv(FILEFOLDER + '/' + filename + '.csv', sep=';')
        writelabelsdata(filename, labels, platforms)
        id -= 1

    #path = '2017_08_22 22_11_12.sig'
    #result = Sig.getdata(path)
    #filename = os.path.splitext(path)[0]
    #result.to_csv(FILEFOLDER + '/' + filename + '.csv', sep=';')
    #writelabelsdata(filename, 0)
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

if __name__ == '__main__':
    main()

