import os
import shutil
import json

FOLDER_ROOT = '/mnt/data/data/LSTM-RL/rs/'
FOLDER_BSP = 'bsp'
FOLDER_BAX = 'bax'
FOLDER_GOOD = 'gd'
FOLDER_FULL = 'fl/'
FOLDER_EMPTY = 'ep/'


def main():
    if not os.path.exists(FOLDER_ROOT + FOLDER_EMPTY):
        os.makedirs(FOLDER_ROOT + FOLDER_EMPTY)
    if not os.path.exists(FOLDER_ROOT + FOLDER_FULL):
        os.makedirs(FOLDER_ROOT + FOLDER_FULL)

    if not os.path.exists(FOLDER_ROOT + FOLDER_FULL + FOLDER_BSP):
        os.makedirs(FOLDER_ROOT + FOLDER_FULL + FOLDER_BSP)
    if not os.path.exists(FOLDER_ROOT + FOLDER_FULL + FOLDER_BAX):
        os.makedirs(FOLDER_ROOT + FOLDER_FULL + FOLDER_BAX)
    if not os.path.exists(FOLDER_ROOT + FOLDER_FULL + FOLDER_GOOD):
        os.makedirs(FOLDER_ROOT + FOLDER_FULL + FOLDER_GOOD)

    if not os.path.exists(FOLDER_ROOT + FOLDER_EMPTY + FOLDER_BSP):
        os.makedirs(FOLDER_ROOT + FOLDER_EMPTY + FOLDER_BSP)
    if not os.path.exists(FOLDER_ROOT + FOLDER_EMPTY + FOLDER_BAX):
        os.makedirs(FOLDER_ROOT + FOLDER_EMPTY + FOLDER_BAX)
    if not os.path.exists(FOLDER_ROOT + FOLDER_EMPTY + FOLDER_GOOD):
        os.makedirs(FOLDER_ROOT + FOLDER_EMPTY + FOLDER_GOOD)

    for file in os.listdir(FOLDER_ROOT + 'jsn'):
        f = open(FOLDER_ROOT + 'jsn/' + file)
        data = json.load(f)
        f.close()
        filename = os.path.splitext(file)[0] + '.csv'
        print(filename)
        if data['full']:
            file_ef = FOLDER_FULL
        else:
            file_ef = FOLDER_EMPTY
        if data['badaxle']:
            shutil.copy(FOLDER_ROOT + 'csv/' + filename, FOLDER_ROOT + file_ef + FOLDER_BAX + '/' + filename)
            continue
        if data['badspeed']:
            shutil.copy(FOLDER_ROOT + 'csv/' + filename, FOLDER_ROOT + file_ef + FOLDER_BSP + '/' + filename)
            continue
        shutil.copy(FOLDER_ROOT + 'csv/' + filename, FOLDER_ROOT + file_ef + FOLDER_GOOD + '/' + filename)


if __name__ == '__main__':
    main()
