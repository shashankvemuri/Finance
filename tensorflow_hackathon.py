from __future__ import absolute_import, division, print_function, unicode_literals

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
import imageio
from PIL import Image
import matplotlib.image as img
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
from resizeimage import resizeimage
import cv2
from concurrent import futures
import threading
from sklearn.model_selection import train_test_split
from collections import Counter
import numpy as np
import pandas as pd


i = 0
arr_infected =[]

for filename in os.listdir("/Users/shashank/Desktop/cell_images/Parasitized/"):
    if filename.endswith(".png") or filename.endswith(".py"): 
        print(str(i) + "picture Parasitized")
        i+=1
        arr_infected.append(cv2.imread("/Users/shashank/Desktop/cell_images/Parasitized/" + filename))
        if len(arr_infected) == 500:
            break
        continue
    else:
        continue
    
i = 0
#arr_uninfected = []
for filename in os.listdir("/Users/shashank/Desktop/cell_images/Uninfected/"):
    if filename.endswith(".png") or filename.endswith(".py"): 
        print(str(i) + "picture Uninfected")
        i+=1
        arr_infected.append(cv2.imread("/Users/shashank/Desktop/cell_images/Uninfected/" + filename))
        if len(arr_infected) == 1000:
            break
        continue
    else:
        continue
classNames = []
for i in range(500):
    classNames.append(0)
for i in range(500):
    classNames.append(1)
    
print(len(classNames))
print(classNames)


npa = np.asarray(arr_infected)
npm = np.asarray(classNames)

print(npm.shape)

train_images = npa[0:400]
train_labels = npm[0:400]
test_images = npa[401:500]
test_labels = npm[401:500]

train_images2 = npa[500:900]
train_labels2 = npm[500:900]
test_images2 = npa[901:1001]
test_labels2 = npm[901:1001]

#FULL ARRAYS
trainImages = np.concatenate((train_images,train_images2))
trainLabels = np.concatenate((train_labels,train_labels2))
testImages = np.concatenate((test_images,test_images2))
testLabels = np.concatenate((test_labels,test_labels2))


IMG_DIMS = (125, 125)

def get_img_data_parallel(idx, im, total_imgs):
    if idx % 5000 == 0 or idx == (total_imgs - 1):
        print('{}: working on img num: {}'.format(threading.current_thread().name,
                                                  idx))
    im = cv2.resize(im, dsize=IMG_DIMS, 
                     interpolation=cv2.INTER_CUBIC)
    im = np.array(im, dtype=np.float32)
    return img

for im in arr_infected:
    get_img_data_parallel(800, im, 1000)

#TESTS
print(trainImages.shape)
print(trainLabels.shape)
print(testImages.shape)
print(testLabels.shape)

'''
trainImages = train_images / 255.0
testImages = test_images / 255.0
'''

for i in range(25):
    plt.subplot(5,5,i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(trainImages[i], cmap=plt.cm.binary)
    plt.xlabel(classNames[trainLabels[i]])
    plt.show()

plt.figure(figsize=(10,10))
for i in range(25):
    plt.subplot(5,5,i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(trainImages[i], cmap=plt.cm.binary)
    plt.xlabel(classNames[trainLabels[i]])
plt.show()

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(145, 145)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(10, activation='softmax')
])
    
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(trainImages, trainLabels, epochs=10)

test_loss, test_acc = model.evaluate(testImages, testLabels, verbose=2)

print('\nTest accuracy:', test_acc)
plt.imshow(arr_infected[10])
