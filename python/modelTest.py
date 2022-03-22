# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 18:38:04 2022

@author: yadlo
"""
#Use only CPU
import os 
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import pandas
import tools

NO2Path = r"C:\Users\yadlo\Desktop\Year 3\Project\python\data\NO2Data.csv"
NO2Data = pandas.read_csv(NO2Path)
NO2Data.drop('Unnamed: 0', axis=1, inplace=True)
NO2Data['date'] = pandas.to_datetime(NO2Data['date'], format='%Y-%m-%d %H:%M:%S')
NO2Data = NO2Data.set_index('date')

NO2Data.info()

train, valid, test = tools.trainTestSplit(0.7, 0.1, NO2Data)

scaledTrain, scaledValid, scaledTest = tools.scaleData(train, valid, test)

nFeatures = 6
window = 7

trainX, trainY = tools.createWindow(scaledTrain, window)
validX, validY = tools.createWindow(scaledValid, window)
testX, testY = tools.createWindow(scaledTest, window)

print(trainX.shape[1], trainY.shape)

model = tools.createInitialModel(features=nFeatures, window=7)

history = model.fit(trainX, trainY, validation_data=(validX, validY),
                    epochs=100)

tools.plotPredictions(model, testX, testY)
tools.plotLoss(history)

model.save(r'C:\Users\yadlo\Desktop\Year 3\Project\python\models\myModel')