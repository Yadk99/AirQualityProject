# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 13:55:36 2022

@author: yadlo
"""

import pandas
import tools
from keras.models import load_model
from keras.callbacks import ModelCheckpoint, EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer

path = r"C:\Users\yadlo\Desktop\Year 3\Project\python\data\allData.csv"
dataset = pandas.read_csv(path)
dataset.drop('Unnamed: 0', axis=1, inplace=True)
dataset['date'] = pandas.to_datetime(dataset['date'], format='%Y-%m-%d %H:%M:%S')
dataset = dataset.set_index('date')

modelPath = r'C:\Users\yadlo\Desktop\Year 3\Project\python\models\finalModel'

#ignore ceratin columns for scaling, as they are already between 0 and 1
cols = [col for col in dataset.columns if col not in ['coKens', 'coMary']]

train, valid, test = tools.trainTestSplit(0.7, 0.1, dataset)

scaler = ColumnTransformer(remainder='passthrough', transformers=[
  ('minmax', MinMaxScaler(), cols)])

minmax = scaler.named_transformers_['minmax']

def scaleData(train, valid, test): 
  scaler.fit(train)
  scaledTrain = scaler.transform(train)
  scaledValid = scaler.transform(valid)
  scaledTest = scaler.transform(test)
  return scaledTrain, scaledValid, scaledTest

def inverseValues(data):
  #[0] indicates the value that is being used as the function, [0] = no2,
  #[1] = o3, [2] = so2, [3] = pm2.5, [12] = co
  inverse = (data * minmax.data_range_[0]) + minmax.data_min_[0]
  return inverse

#moves columns to end of array
scaledTrain, scaledValid, scaledTest = scaleData(train, valid, test)

window = 7

#NO2 - done, o3 - done, so2 - 
trainX, trainY = tools.createWindow(scaledTrain, window)
validX, validY = tools.createWindow(scaledValid, window)
testX, testY = tools.createWindow(scaledTest, window)

#run once only, to create inital network then train
model2 = tools.createInitialModel(features=14, window = window)
#otherwise load model
model2 = load_model(modelPath, compile=(True))

valStop = EarlyStopping(monitor='val_loss', patience=10)
checkpoint = ModelCheckpoint(modelPath, monitor='val_loss')

history = model2.fit(trainX, trainY, validation_data=(validX, validY),
                     epochs=100, callbacks=[valStop, checkpoint])

NO2preds = tools.plotPredictions(model2, testX, testY)
NO2preds['Actual'] = inverseValues(NO2preds['Actual'])
NO2preds['Predictions'] = inverseValues(NO2preds['Predictions'])
NO2preds.tail

O3preds = tools.plotPredictions(model2, testX, testY)
O3preds['Actual'] = inverseValues(O3preds['Actual'])
O3preds['Predictions'] = inverseValues(O3preds['Predictions'])
test['o3Kens'].tail

SO2preds = tools.plotPredictions(model2, testX, testY)
SO2preds['Actual'] = inverseValues(SO2preds['Actual'])
SO2preds['Predictions'] = inverseValues(SO2preds['Predictions'])
SO2preds.tail

pm25preds = tools.plotPredictions(model2, testX, testY)
pm25preds['Actual'] = inverseValues(pm25preds['Actual'])
pm25preds['Predictions'] = inverseValues(pm25preds['Predictions'])
pm25preds.tail

COpreds = tools.plotPredictions(model2, testX, testY)
COpreds.tail

tools.plotLoss(history)

model2.save(r'C:\Users\yadlo\Desktop\Year 3\Project\python\models\finalModel')