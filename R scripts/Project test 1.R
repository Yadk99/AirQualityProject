library(tidyverse)

AirQuality =  read.csv('C:\\Users\\yadlo\\Desktop\\Year 3\\Project\\R scripts\\Project test 1\\EalingJan2020to2021Clean.csv')

# converting string datetime into R datetime data type
AirQuality$ReadingDateTime <- lubridate::dmy_hm(AirQuality$ReadingDateTime)

summary(AirQuality)

# drop NA values, better to impute as dropping NA will interrupt the time steps
# and may remove rows that may only be missing one variable
AirQuality %>% 
  drop_na() %>%
  summary() 

# plotting graphs to capture trend and a line graph
airQualityLine <- ggplot(data = AirQuality, aes(ReadingDateTime)) + scale_y_log10() +
  geom_line(aes(y = NO), color = "Red") +
  geom_line(aes(y = NO2), colour = "Green") +
  geom_line(aes(y = NOX), colour = "Black") +
  geom_line(aes(y = PM10), colour = "Blue")
  
airQualityLine

airQualityTrend <-ggplot(data = AirQuality, aes(ReadingDateTime)) + scale_y_log10() +
  geom_smooth(aes(y = NO), colour = "red",se=FALSE) +
  geom_smooth(aes(y = NO2), colour = "green", se=FALSE) +
  geom_smooth(aes(y = NOX), colour = "black", se=FALSE) +
  geom_smooth(aes(y = PM10), colour = "blue", se=FALSE)

airQualityTrend

cor(AirQuality[2:5],)

AirQuality$month = lubridate::floor_date(AirQuality$ReadingDateTime, "month")

# creating monthly average dataframe
monthlyNOAvg <- AirQuality %>%
  group_by(month) %>%
  summarise(NOmean = mean(NO)) %>%
  as.data.frame()

monthlyNOPlot <- ggplot(data = monthlyNOAvg, aes(month)) + scale_y_continuous() +
  geom_point(aes(y=NOmean), colour = "Red") + 
  geom_line(aes(y=NOmean))

monthlyNOPlot

library(tsbox)
library(forecast)

# tsbox allows us to convert dataframes into time series objects, here the datetime
# and corresponding data are converted to a time series object
AirQualitySample <- ts_ts(AirQuality[,1:2])
# creating a test and training set
AirQualityTrain <- AirQualitySample[1:300]
AirQualityTest <- AirQualitySample[301:366]

# autoplot will automatically plot any data against time in a time series object
autoplot(AirQualitySample)

# nnetar creates a feed forward neural network which can only go forward, unlike
# alternatives such as RNN
model <- nnetar(AirQualityTrain)
# once the model is trained we make it predict 66 steps ahead, to match the test
# set
modelPlot <- forecast(model, h = 66)

autoplot(modelPlot) 

#plotting the actual results against the predicted results
modelPlotandActual <- ggplot(data = AirQuality[,1:2], aes(ReadingDateTime)) + scale_y_continuous() +
  geom_line(aes(y=NO), colour = "red") +
  geom_line(aes(modelPlot$mean), colour = "blue")
modelPlotandActual
