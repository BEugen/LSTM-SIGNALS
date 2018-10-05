from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import SGD, Adam, RMSprop
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import img_to_array
import cv2, numpy as np
import os
from keras.callbacks import TensorBoard
from time import time
import random


WINDOW_SIZE = 50
IMG_PATH_TRAIN = 'Imagetrain/train/'
IMG_PATH_TEST= 'Imagetrain/test/'
#IMG_PATH = 'Imgtrain/'
BATCH_SIZE = 128
NB_EPOCH = 76
NB_CLASSES = 2
VERBOSE = 1
VALIDATION_SPLIT = 0.25
INIT_LR = 1e-3
OPTIM = Adam()#Adam(lr=INIT_LR, decay=INIT_LR / NB_EPOCH)





def LSTM():


    return model




def load_data(path):

    return x_data, y_data


def main():
    X_train, Y_train = load_image(IMG_PATH_TRAIN)
    Y_train = np_utils.to_categorical(Y_train, num_classes=3)
    X_test, Y_test = load_image(IMG_PATH_TEST)
    Y_test= np_utils.to_categorical(Y_test, num_classes=3)
    #(X_train, X_test, Y_train, Y_test) = train_test_split(X, Y, test_size=.25, random_state=40)

    tensorboard = TensorBoard(log_dir="logs/{}".format(time()), write_graph=True, write_grads=True, write_images=True,
                              histogram_freq=0)
    # fit
    model = LeNet()
    model.compile(loss='categorical_crossentropy', optimizer=OPTIM, metrics=['accuracy'])
    history = model.fit(X_train, Y_train, batch_size=BATCH_SIZE, epochs=NB_EPOCH, verbose=VERBOSE,
                        validation_data=(X_test, Y_test),
                        validation_split=VALIDATION_SPLIT, callbacks=[tensorboard])

    score = model.evaluate(X_test, Y_test, verbose=VERBOSE)
    print('Test score:', score[0])
    print('Test accuracy', score[1])

    # save model
    model_json = model.to_json()
    with open("model_ln_4.json", "w") as json_file:
        json_file.write(model_json)
        #serialize weights to HDF5
    model.save_weights("model_ln_4.h5")


if __name__ == '__main__':
    main()
