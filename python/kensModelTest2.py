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

path = r"C:\Users\yadlo\Desktop\Year 3\Project\python\kensDataDaily.csv"

kensDailyData = pandas.read_csv(path)

# date in the dataset is loaded as a string, converting it to python datetime
pandas.to_datetime(kensDailyData['date'])

kensDailyData.drop('Unnamed: 0', axis=1, inplace=True)
plt.figure(figsize=(16,8))
kensDailyData.head()

kensDailyData.plot()

df = kensDailyData.drop(['o3', 'pm2.5'], axis=1)

from statsmodels.tsa.seasonal import seasonal_decompose

df.info()
df['date'] = pandas.to_datetime(df['date'])
df = df.set_index('date').asfreq('D')
seasonalData = seasonal_decompose(df, model='additive')

seasonalData.plot()

# function that will split data into train and test set
def trainTestSplit(trainProportion, data):
    trainNum = int(len(data)*trainProportion)
    train = data[:trainNum]
    test = data[trainNum:]
    return train, test
    
train, test = trainTestSplit(0.8, df)

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scaler.fit(train)
scaledTrain = scaler.transform(train)
scaledTest = scaler.transform(test)

from keras.preprocessing.sequence import TimeseriesGenerator

nInput = 7
nFeatures = 1

generator = TimeseriesGenerator(scaledTrain, scaledTrain, length=nInput,
                                batch_size=64)

print(generator[0])

model = Sequential()
model.add(LSTM(120, activation = 'tanh', input_shape= (nInput, nFeatures),
                return_sequences=True))
model.add(LSTM(120, activation='tanh', input_shape= (nInput, nFeatures),  
                return_sequences=False))
model.add(Dense(1, activation = 'sigmoid'))
model.compile(optimizer='adam', loss='mse')

# model = Sequential()
# model.add(Dense(80, activation = 'relu'))
# model.add(Dense(80, activation='relu'))
# model.add(Dense(1, activation = 'sigmoid'))
# model.compile(optimizer='adam', loss='mse')

model.summary()

model.fit(generator, epochs=1500)

modelLoss = model.history.history['loss']
plt.plot(modelLoss)

testPredictions = []
firstEvalBatch = scaledTrain[-nInput:]
currentBatch = firstEvalBatch.reshape(1, nInput, nFeatures)
print(currentBatch.shape)

for i in range(len(test)):
    currentPrediction = model.predict(currentBatch)[0]
    testPredictions.append(currentPrediction)
    currentBatch = numpy.append(currentBatch[:,1:,:],[[currentPrediction]],
                              axis = 1)

# for i in range(len(test)):
#     currentPrediction = model.predict(currentBatch)[0]
#     testPredictions.append(currentPrediction)
#     currentBatch = numpy.append(currentBatch, currentPrediction)
#     currentBatch = numpy.delete(currentBatch, 0)
#     currentBatch = currentBatch.reshape(7,1)

modelLoss.reshape(-1,1)
truePredictions = scaler.inverse_transform(testPredictions)
trueLoss = scaler.inverse_transform(modelLoss)

test['predictions'] = truePredictions
test.plot()

from keras.utils.vis_utils import plot_model

plot_model(model, show_layer_activations=(True), show_shapes=(True))
