#!/usr/bin/python

# Python code for flask web app
# multiclass model (5 classes)

from keras.preprocessing import image
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as immg

# input is image you want to classify
# predicts class of image


def equipred(img_save_path):
    # dimensions of our images.
    img_width, img_height = 150, 150

    # load image you want to make prediction for
    img = image.load_img(img_save_path, target_size=(img_width, img_height))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255

    if K.image_data_format() == 'channels_first':
        input_shape = (3, img_width, img_height)
    else:
        input_shape = (img_width, img_height, 3)

    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=input_shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(10))
    model.add(Activation('softmax'))

    # load weights into new model
    model.load_weights(
        'sport_name.h5')

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    pred = model.predict(img_tensor)

    index_predict = np.argmax(pred[0])

    # if probabilities are spread out and there's no clear winner, return "unsure"
    if pred[0][index_predict] <= 0.50:
        return "unsure"

    dict_labels = {0: 'Abductor&AdductorMachine 大腿內收外展機', 1: 'BicepsCurlMachine 二頭彎舉機', 2: 'CableMachine 滑輪訓練機', 3: 'ChestFlyMachine 蝴蝶機', 4: 'HackSquatMachine 哈克深蹲機',
                   5: 'LegPressMachine 腿部推舉機', 6: 'LegRaiseMachine 雙槓抬腿機', 7: 'RowingMachine 划船機', 8: 'SittingLegPressMachine 坐式腿推機', 9: 'SmithMachine 史密斯架'}


    return dict_labels[index_predict]

def main():
    print('hi')

if __name__ == '__main__':
    main()
