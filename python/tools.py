# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 15:48:21 2022

@author: yadlo
"""
import pandas
import tensorflow
import numpy
import matplotlib.pyplot as plt
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout, GRU, SimpleRNN
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()

# function that will split data into train and test set
def trainTestSplit(trainProportion, testProportion, data):
    dataLength = int(len(data))
    trainNum = int(dataLength*trainProportion)
    testNum = int(dataLength*testProportion)
    train = data[0:trainNum]
    valid = data[trainNum:(dataLength-testNum)]
    test = data[:testNum]
    return train, valid, test
  
def scaleData(train, valid, test):
 
  scaler.fit(train)
  scaledTrain = scaler.transform(train)
  scaledValid = scaler.transform(valid)
  scaledTest = scaler.transform(test)
  return scaledTrain, scaledValid, scaledTest

def createWindow(df, windowSize):
  data = []
  target = []
  for i in range(len(df) - windowSize):
    row = [r for r in df[i:i+windowSize]]
    data.append(row)
    label = [df[i+windowSize][0]]
    target.append(label)
  return numpy.array(data), numpy.array(target)

def createInitialModel(features, window):
  model = Sequential()
  model.add(LSTM(80, activation='relu', return_sequences=True, 
                 input_shape=(features, window)))
  model.add(LSTM(80, activation='relu', return_sequences=False))
  model.add(Dense(1, activation='sigmoid'))
  #default learning rate = 0.001
  model.compile(optimizer='adam', loss='mse')
  return model

def inverseValues(data):
  inversed = scaler.data_range_[:1] * data + scaler.data_min_[:1]
  return inversed

def plotPredictions(model, data, target):
  predictions = model.predict(data)
  predictions = predictions.flatten()
  actual = target[:,0]
  realPredictions = inverseValues(predictions)
  realActual = inverseValues(actual)
  df = pandas.DataFrame(data = {'Predictions': realPredictions,
                                'Actual': realActual})
  plt.plot(df['Predictions'], label = 'Predicted Values')
  plt.plot(df['Actual'], label = 'Actual Values')
  plt.xlabel('Day')
  plt.ylabel('NO2 (µg/m3)')
  plt.legend()
  
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