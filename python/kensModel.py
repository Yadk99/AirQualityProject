import pandas
import tensorflow
import numpy
import matplotlib.pyplot as plt
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

path = r"C:\Users\yadlo\Desktop\Year 3\Project\python\kensDataDaily.csv"

kensDailyData = pandas.read_csv(path, index_col=False)

# date in the dataset is loaded as a string, converting it to python datetime
pandas.to_datetime(kensDailyData['date'])

print(kensDailyData.head())

# creating plots for each variable
kensDailyData.set_index('date')[["no2", "o3", "pm2.5"]].plot(subplots=True)

plt.show()

print(kensDailyData.shape)

# function that will split data into train and test set
def trainTestSplit(trainProp, data):
    trainNum = int(len(data)*trainProp)
    train = data[:trainNum]
    test = data[trainNum:]
    return train, test
    
train, test = trainTestSplit(0.8, kensDailyData)

print(train.head)

# scaling data down so it can be used in NN
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaler.fit(train[['no2','o3', 'pm2.5']])
scaledTrain = scaler.transform(train[['no2','o3', 'pm2.5']])
scaledTest = scaler.transform(test[['no2','o3', 'pm2.5']])

# fit the scaler to just one variable to see if it would help the prediction
# (it didnt)
scaler.fit(train[['no2']])

from keras.preprocessing.sequence import TimeseriesGenerator

# TimeseriesGenerator will only support univariate output, so i have only used
# one variable at the moment
trainNo2 = scaledTrain[:,0].copy()
testNo2 = scaledTest[:,0].copy()

# number of inputs to be used to output one step
nInput = 30
# number of variables in the dataset, should be one unless I find a way to 
# do multivariable output using TimeseriesGenerator
nFeatures = 1

# Timeseriesgenerator will return a Sequence object, converting data into a 
# supervised learning problem, i i+1 i+2 -> i+3 and so on
generator = TimeseriesGenerator(trainNo2, trainNo2, length=nInput, 
                                batch_size=1)

# can the inputs and outputs of the generator by calling an index
initialInput, initialOutput = generator[0]

# adding layers to the neural network
modelNo2 = Sequential()
# LSTM = Long Short Term Memory, contain 'memory cell' that should be advantageous
# over long periods of time
modelNo2.add(LSTM(10, activation='relu', input_shape=(nInput, nFeatures)))
modelNo2.add(Dropout(0.2))
modelNo2.add(Dense(1, activation='relu'))
modelNo2.compile(optimizer='adam', loss='mse')

modelNo2.summary()

# with these parameters loss function was reaching minimum at around 4-6 epochs
# i used 5 just to save time
modelNo2.fit(generator, epochs=5)

#manually testing the last to be fed into the model
lastTrainBatch = trainNo2[-(nInput):]

lastTrainBatch = lastTrainBatch.reshape(1, nInput, nFeatures)

modelNo2.predict(lastTrainBatch)
print(testNo2[0])

#preparing variable and loop to add the predicted values into a list
currentBatch = lastTrainBatch

testPredictions = []

for i in range(len(testNo2)):
    currentPrediction = modelNo2.predict(currentBatch)[0]
    testPredictions.append(currentPrediction)
    currentBatch = numpy.append(currentBatch[:,1:,:],[[currentPrediction]],
                                axis=1)

# reversing the scaling of the data
realPrediction =  scaler.inverse_transform(testPredictions)
# creating a dataframe of the original data and the predictions
finalDatasetNo2 = test['no2'].to_frame()
realp = realPrediction.flatten()
realp = realp.tolist()
finalDatasetNo2.insert(loc=1, column='prediction', value = realp)
finalDatasetNo2.plot()
