# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 13:55:36 2022

@author: yadlo
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import pandas
import tools
from keras.models import load_model
from keras.utils.vis_utils import plot_model
from keras.callbacks import ModelCheckpoint, EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer

path = r".\data\allData.csv"
dataset = pandas.read_csv(path, index_col=(0))
dataset['date'] = pandas.to_datetime(dataset['date'], format='%Y-%m-%d %H:%M:%S')
dataset = dataset.set_index('date')

modelPath = r'.\models\finalModel'
testModelPath = r'.\models\testModel'

#ignore certain columns for scaling, as they are already between 0 and 1
cols = [col for col in dataset.columns if col not in ['coKens', 'coMary']]

train, valid, test = tools.trainTestSplit(0.7, 0.1, dataset)

scaler = ColumnTransformer(remainder='passthrough', transformers=[
  ('minmax', MinMaxScaler(), cols)])

def scaleData(train, valid, test): 
  scaler.fit(train)
  scaledTrain = scaler.transform(train)
  scaledValid = scaler.transform(valid)
  scaledTest = scaler.transform(test)
  return scaledTrain, scaledValid, scaledTest

#moves CO columns to end of array
scaledTrain, scaledValid, scaledTest = scaleData(train, valid, test)

minmax = scaler.named_transformers_['minmax']

window = 7

#no2 - done, o3 - done, so2 - done, pm25 - done  
trainX, trainY = tools.createWindow(scaledTrain, window)
validX, validY = tools.createWindow(scaledValid, window)
testX, testY = tools.createWindow(scaledTest, window)

#run once only, to create inital network then train
model2 = tools.createInitialModel(features=14, window = window)
#otherwise load model
model2 = load_model(modelPath, compile=(True))

valStop = EarlyStopping(monitor='val_loss', patience=30)
checkpoint = ModelCheckpoint(testModelPath, monitor='val_loss', save_best_only=(True))

history = model2.fit(trainX, trainY, validation_data=(validX, validY),
                     epochs=200, callbacks=[checkpoint, valStop])

def inverseValues(data):
  #[0] indicates the value that is being used as the function, [0] = no2,
  #[1] = o3, [8] = so2, [3] = pm2.5
  inverseConstants = {'NO2':0, 'O3':1, 'SO2':8, 'PM2.5':9}
  for col in data:
    pollutant = col.split(" ")[0]
    if pollutant == 'CO':
      break
    inverse = (data[col] * minmax.data_range_[inverseConstants[pollutant]]) \
      + minmax.data_min_[inverseConstants[pollutant]]
    print(inverse)  
    data[col] = inverse
  return data
      

predictions = tools.getPredictions(model2, testX, testY)

realPredictions = inverseValues(predictions)

predictions.columns

predictions.tail

tools.plotLoss(history)

plot_model(model2, show_shapes=(True), show_layer_activations=(True))

model2.save(r'.\finalModel')

realPredictions.to_csv(r".\data\preds3.csv")
