# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 18:38:04 2022

@author: yadlo
"""
#Use only CPU
import os 
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import pandas
import tensorflow
import numpy
import matplotlib.pyplot as plt
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout, GRU, SimpleRNN
from keras.callbacks import EarlyStopping, ModelCheckpoint
from time import time
import tools

NO2Path = r"C:\Users\yadlo\Desktop\Year 3\Project\python\data\NO2Data.csv"
NO2Data = pandas.read_csv(NO2Path)
NO2Data.drop('Unnamed: 0', axis=1, inplace=True)
NO2Data['date'] = pandas.to_datetime(NO2Data['date'], format='%Y-%m-%d %H:%M:%S')
NO2Data = NO2Data.set_index('date')

NO2Data.info()

train, valid, test = tools.trainTestSplit(0.7, 0.1, NO2Data)

tools.scaler.fit(train)
scaledTrain = tools.scaler.transform(train)
scaledValid = tools.scaler.transform(valid)
scaledTest = tools.scaler.transform(test)

nFeatures = 6
window = 6

trainX, trainY = tools.createWindow(scaledTrain, window)
validX, validY = tools.createWindow(scaledValid, window)
testX, testY = tools.createWindow(scaledTest, window)

print(trainX.shape[1], trainY.shape)

model = tools.createInitialModel(nFeatures, 6)

history = model.fit(trainX, trainY, validation_data=(validX, validY),
                    epochs=90)

tools.plotPredictions(model, testX, testY)
tools.plotLoss(history)

model.save(r'C:\Users\yadlo\Desktop\Year 3\Project\python\models\myModel')
