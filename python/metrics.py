# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 13:11:35 2022

@author: yadlo
"""

import pandas
import tools
import matplotlib.pyplot as plt

path = r"./data/preds2.csv"

preds = pandas.read_csv(path, index_col=0)

no2Metrics = tools.calculateMetrics(preds, 'NO2')
o3Metrics = tools.calculateMetrics(preds, 'O3')
so2Metrics = tools.calculateMetrics(preds, 'SO2')
pm25Metrics = tools.calculateMetrics(preds, 'PM2.5')
coMetrics = tools.calculateMetrics(preds, 'CO')

metricsData = {'NO2': no2Metrics,
               'O3': o3Metrics,
               'SO2': so2Metrics,
               'PM2.5': pm25Metrics,
               'CO': coMetrics}

metricsDf = pandas.DataFrame(metricsData)

metricsDf.to_csv(r".\data\Finalmetrics.csv")


dfPath = r".\data\allData.csv"

allData = pandas.read_csv(dfPath, index_col = 0)

#creating dataframe for O3 to get full scope of predictions
O3data = pandas.DataFrame({'date' : allData['date'],
                           'O3 Actual' : allData['o3Kens']})

O3preds = pandas.DataFrame(columns =['date',
                            'O3 Predicted'])

#matching the indexes for predictions and actual
O3preds['date'] = O3preds['date'].append(allData['date'].tail(248), ignore_index=True)
O3preds['O3 Predicted'] = preds['O3 Predictions']

O3preds.head

O3data['date'] = pandas.to_datetime(O3data['date'], format='%Y-%m-%d')
O3preds['date'] = pandas.to_datetime(O3preds['date'], format='%Y-%m-%d')

O3data = O3data.set_index('date')
O3preds = O3preds.set_index('date')

O3data.tail
O3preds.tail

#plotting both on the same graph
plt.plot(O3data, label = 'Actual Values')
plt.plot(O3preds, label = 'Predicted Values')
plt.xlabel('Time')
plt.ylabel('O3 (µg/m3)')
plt.legend()

#creating a date index for predcitions to plot
preds['date'] = None

preds['date'] = allData.tail(248).to_numpy()

preds['date'] = pandas.to_datetime(preds['date'], format='%Y-%m-%d')
preds = preds.set_index('date')

#plotted each pollutant manually
plt.plot(preds[['CO Predictions', 'CO Actual']])
plt.xlabel('Date')
plt.ylabel('CO (PPM)')
plt.legend(['Predicted Values', 'Actual Values'])