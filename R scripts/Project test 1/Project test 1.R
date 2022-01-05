library(tidyverse)

AirQuality =  read.csv('C:\\Users\\yadlo\\Desktop\\Year 3\\Project\\R scripts\\Project test 1\\EalingJan2020to2021Clean.csv')

AirQuality$ReadingDateTime <- lubridate::dmy_hm(AirQuality$ReadingDateTime)

summary(AirQuality)

AirQuality %>% 
  drop_na() %>%
  summary() 

AirQuality %>%
  filter()

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

AirQualitySample <- ts_ts(AirQuality[,1:2])
AirQualityTrain <- AirQualitySample[1:300]
AirQualityTest <- AirQualitySample[301:366]

autoplot(AirQualitySample)

model <- nnetar(AirQualityTrain)
modelPlot <- forecast(model, h = 66)
modelPlot$mean

autoplot(modelPlot) 

modelPlotandActual <- ggplot(data = AirQuality[,1:2], aes(ReadingDateTime)) + scale_y_continuous() +
  geom_line(aes(y=NO), colour = "red") +
  geom_line(aes(modelPlot$mean), colour = "blue")
modelPlotandActual
