import os
import shutil
import json

FOLDER_ROOT = 'E:/TMP/rs/'
FOLDER_BSP = 'bsp'
FOLDER_BAX = 'bax'
FOLDER_GOOD = 'gd'



def main():
    if not os.path.exists(FOLDER_ROOT + FOLDER_BSP):
        os.makedirs(FOLDER_ROOT + FOLDER_BSP)
    if not os.path.exists(FOLDER_ROOT + FOLDER_BAX):
        os.makedirs(FOLDER_ROOT + FOLDER_BAX)
    if not os.path.exists(FOLDER_ROOT + FOLDER_GOOD):
        os.makedirs(FOLDER_ROOT + FOLDER_GOOD)
    for file in os.listdir(FOLDER_ROOT + 'jsn'):
        f = open(FOLDER_ROOT + 'jsn/' + file)
        data = json.load(f)
        f.close()
        filename = os.path.splitext(file)[0] + '.csv'
        print(filename)
        if data['badaxle']:
            shutil.copy(FOLDER_ROOT + 'csv/' + filename, FOLDER_ROOT + FOLDER_BAX + '/' + filename)
            continue
        if data['badspeed']:
            shutil.copy(FOLDER_ROOT + 'csv/' + filename, FOLDER_ROOT + FOLDER_BSP + '/' + filename)
            continue
        shutil.copy(FOLDER_ROOT + 'csv/' + filename, FOLDER_ROOT + FOLDER_GOOD + '/' + filename)


if __name__ == '__main__':
    main()
