# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 15:48:21 2022

@author: yadlo
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 
import pandas
import numpy
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, LSTM
import tensorflow as tf 
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from scipy.stats import pearsonr

# function that will split data into train and test set
def trainTestSplit(trainProportion, testProportion, data):
    dataLength = int(len(data))
    trainNum = int(dataLength*trainProportion)
    testNum = int(dataLength*testProportion)
    train = data[0:trainNum]
    valid = data[trainNum:(dataLength-testNum)]
    test = data[-(testNum):]
    return train, valid, test
  
def createWindow(df, windowSize):
  data = []
  target = []
  #as the loop starts with the first x values, it needs to stop before going 
  #out of bounds
  for i in range(len(df) - windowSize):
    #take x amount of rows and append to the data
    row = [r for r in df[i:i+windowSize]]
    data.append(row)
    #[0] indicates the column that is being used as the label, [0] = no2,
    #[1] = o3, [8] = so2, [3] = pm2.5, [13] = co
    #the next value will be used as the label, therefore +windowSize
    label = [df[i+windowSize][0], df[i+windowSize][1], df[i+windowSize][8],
             df[i+windowSize][3], df[i+windowSize][13]]
    target.append(label)
  return numpy.array(data), numpy.array(target)

def createInitialModel(features, window):
  model = Sequential()
  model.add(LSTM(40, activation='tanh', return_sequences=True, 
                 input_shape=(window, features)))
  model.add(LSTM(40, activation='tanh', return_sequences=False))
  model.add(Dense(5, activation='sigmoid'))
  #default learning rate = 0.001
  opt = tf.keras.optimizers.Adam(learning_rate=0.01)
  model.compile(optimizer=opt, loss='mse')
  return model

def getPredictions(model, data, target):
  predictions = model.predict(data)
  #slice the 2d array by the column to create a 1d array
  no2Preds, o3Preds, so2Preds, pm25Preds, coPreds = predictions[:,0], predictions[:,1], predictions[:,2], predictions[:,3], predictions[:,4]
  no2Actual, o3Actual, so2Actual, pm25Actual, coActual = target[:,0], target[:,1], target[:,2],target[:,3],target[:,4]
  df = pandas.DataFrame(data = {'NO2 Predictions': no2Preds,
                                'NO2 Actual': no2Actual,
                                'O3 Predictions': o3Preds,
                                'O3 Actual': o3Actual,
                                'SO2 Predictions': so2Preds,
                                'SO2 Actual': so2Actual,
                                'PM2.5 Predictions': pm25Preds,
                                'PM2.5 Actual': pm25Actual,
                                'CO Predictions': coPreds,
                                'CO Actual': coActual})
  return df
  
def plotLoss(modelHistory):
  valLoss = modelHistory.history['val_loss']
  loss = modelHistory.history['loss']
  df= pandas.DataFrame(data = {'Training Loss': loss,
                               'Validation Loss': valLoss})
  plt.plot(df['Training Loss'], label = 'Training Loss')
  plt.plot(df['Validation Loss'], label = 'Validation Loss')
  plt.xlabel('Epoch')
  plt.ylabel('Loss')
  plt.legend()
  
def calculateMetrics(df, pollutant):
  metrics = []
  
  mse = mean_squared_error(df[pollutant + ' Actual'], df[pollutant + ' Predictions'])
  rmse = mean_squared_error(df[pollutant + ' Actual'], df[pollutant + ' Predictions'], squared=(False))
  mae = mean_absolute_error(df[pollutant + ' Actual'], df[pollutant + ' Predictions'])
  mape = 100 * mean_absolute_percentage_error(df[pollutant + ' Actual'], df[pollutant + ' Predictions'])
  r2 = r2_score(df[pollutant + ' Actual'], df[pollutant + ' Predictions'])
  r = pearsonr(df[pollutant + ' Actual'], df[pollutant + ' Predictions'])
  
  metrics.extend((mse, rmse, mae, mape, r2, r))
  
  return metrics