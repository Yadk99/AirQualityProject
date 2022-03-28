library(openair)
library(tidyverse)
library(Amelia)
library(imputeTS)
library(corrplot)

londonDataAURN <- read.csv("C:\\Users\\yadlo\\Desktop\\Year 3\\Project\\Data\\londonDataAURN.csv")
londonDataAURN <- londonDataAURN[,2:15]

summary(londonDataAURN[,4:11])

summaryDf <- data.frame("NA" = c("Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max.", "NAs"),
                        "NO2" = c(-1.66, 15.13, 28.49, 35.26, 38.15, 385.35, 215746),
                        "O3" =  c(-1.3, 17.1, 37.5, 38.2,56.0, 216.5, 536459),
                        "SO2" = c(-2.5, 1.1, 1.9, 3.1, 3.8, 36.7, 734022),
                        "PM2.5" = c(-5, 5, 8, 10.9, 13.4, 236.4, 421697),
                        "CO" = c(0, 0.1, 0.2, 0.3, 0.4,  3.3, 792375),
                        "ws" = c(0, 2.2, 3.1, 3.455, 4.4, 18.6, 30171),
                        "airTemp" = c(-6.8, 5.9, 9.9, 10.18, 14.4, 33.4, 30171))

kensData <- filter(londonDataAURN, londonDataAURN$code == "KC1")
marlData <- filter(londonDataAURN, londonDataAURN$code == "MY1")
bothData <- subset(londonDataAURN, subset = (londonDataAURN$code == "KC1"|londonDataAURN$code == "MY1"))

summary(bothData[,4:11])

filterSummaryDf <- data.frame("NA" = c("Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max.", "NAs"),
                              "NO2"= c(0.2, 19.6, 39.7, 49.2, 68.2, 321.9, 2304),
                              "O3" = c(-0.8, 10.7, 28.7, 33, 50.9, 216.5, 4542),
                              "SO2"= c(-2.5, 1.2, 2.2, 3.6, 4.9, 36.8, 8345),
                              "PM2.5" = c(-4.3, 5.4, 9, 11.9, 15.2, 182.8, 8091),
                              "CO" = c(0, 0.1, 0.2, 0.3, 0.4, 3.3, 14964),
                              "windSpeed" = c(0, 2.2, 3.1, 3.4, 4.3, 12.1, 3048),
                              "airTemp" = c(-6.7, 5.8, 9.9, 10.2, 14.4, 33.4, 3048))

kensData$date <- lubridate::as_datetime(kensData$date)
marlData$date <- lubridate::as_datetime(marlData$date)

summary(kensData)
summary(marlData)

kensMissingWd <- ggplot_na_distribution(kensData$ws, title = "Missing Wind Speed data - North Kensington")
kensMissingWd

kensDataNoNA <- drop_na(kensData)

names(kensDataNoNA)[names(kensDataNoNA) == 'ws'] <- 'windSpeed'
names(kensDataNoNA)[names(kensDataNoNA) == 'wd'] <- 'windDirection'

corrMatrix <- corrplot(cor(kensDataNoNA[,4:11]))#correlation plot, feature selection

sum(kensData$o3<0, na.rm = TRUE)
#should not have negative values, error in data capture
kensDataOnly <- kensData[,4:11]

bound <- rbind(c(1, 0, Inf), c(2, 0, Inf), c(3, 0, Inf), c(4, 0, Inf), c(5, 0, Inf),
               c(6, 0, Inf), c(7, 0, Inf))
#creating bounds for imputation, no negative values

kensDataAmelia <- amelia(kensDataOnly, bounds = bound, m=1)
plot(kensDataAmelia)
missmap(kensDataAmelia)

summary(kensDataAmelia$imputations$imp1)

marlDataAmelia <- amelia(marlData[,4:11], bounds = bound, m=1)
plot(marlDataAmelia)
missmap(marlDataAmelia)

summary(marlDataAmelia$imputations$imp1)

ggplot_na_distribution(kensData[,4])
kensData[names(kensDataAmelia$imputations$imp1)] <- kensDataAmelia$imputations$imp1
summary(kensData)
marlData[names(marlDataAmelia$imputations$imp1)] <- marlDataAmelia$imputations$imp1
summary(marlData)
#data left that is completely missing, cannot be imputed
#to keep temporal integrity, replace with mean values of column, small amount
#therefore small effect on prediction

marlData <- na_mean(marlData)
kensData <- na_mean(kensData)

#replacing negative values, perhaps error in calibration, therefore
#assume that negative values are minimum values that are able to be captured.
#Using EU standard methods, can find how each pollutant is captured and 
#also the minimum value possible to be captured 
# https://uk-air.defra.gov.uk/networks/monitoring-methods?view=eu-standards
#minimum value that is captured is 0, therefore replacing negative values with 0
#https://www.csagroupuk.org/wp-content/uploads/2019/04/MCERTSCertifiedProductsCAMS.pdf

kensData[,4:10][kensData[,4:10] < 0] <- 0
sum(kensData$o3<0, na.rm = TRUE)
marlData[,4:10][marlData[,4:10] < 0] <- 0
sum(marlData$o3<0, na.rm = TRUE)

NO2Data <- kensData[,c(3,5,9:11)]
NO2Data <- rename(NO2Data, no2Kens = no2, wsKens = ws, wdKens = wd, air_tempKens
                  = air_temp)
NO2Data <- cbind(NO2Data, marlData[!names(marlData) %in% names(NO2Data)])
NO2Data <- NO2Data[,c(1:5, 9, 13:15)]
NO2Data <- rename(NO2Data, no2Marl = no2, wsMarl = ws, wdMarl = wd, air_tempMarl
                  = air_temp)
NO2Data <- timeAverage(NO2Data, avg.time = "day", statistic = 'mean')

COData <- kensData[,c(3, 4, 9:11)]
COData <- rename(COData, coKens = co, wsKens = ws, wdKens = wd, air_tempKens
                  = air_temp)
COData <- cbind(COData, marlData[!names(marlData) %in% names(COData)])
COData <- COData[,c(1:5, 8, 13:15)]
COData <- rename(COData, coMarl = co, wsMarl = ws, wdMarl = wd, air_tempMarl
                  = air_temp)
COData <- timeAverage(COData, avg.time = "day", statistic = 'mean')

O3Data <- kensData[,c(3, 6, 9:11)]
O3Data <- rename(O3Data, o3Kens = o3, wsKens = ws, wdKens = wd, air_tempKens
                 = air_temp)
O3Data <- cbind(O3Data, marlData[!names(marlData) %in% names(O3Data)])
O3Data <- O3Data[,c(1:5, 10, 13:15)]
O3Data <- rename(O3Data, o3Marl = o3, wsMarl = ws, wdMarl = wd, air_tempMarl
                 = air_temp)
O3Data <- timeAverage(O3Data, avg.time = "day", statistic = 'mean')

SO2Data <- kensData[, c(3, 7, 9:11)]
SO2Data <- rename(SO2Data, so2Kens = so2, wsKens = ws, wdKens = wd, air_tempKens
                 = air_temp)
SO2Data <- cbind(SO2Data, marlData[!names(marlData) %in% names(SO2Data)])
SO2Data <- SO2Data[, c(1:5, 11, 13:15)]
SO2Data <- rename(SO2Data, so2Marl = so2, wsMarl = ws, wdMarl = wd, air_tempMarl
                 = air_temp)
SO2Data <- timeAverage(SO2Data, avg.time = "day", statistic = 'mean')


PM25Data <- kensData[, c(3, 8:11)]
PM25Data <- rename(PM25Data, pm2.5Kens = pm2.5, wsKens = ws, wdKens = wd, air_tempKens
                  = air_temp)
PM25Data <- cbind(PM25Data, marlData[!names(marlData) %in% names(PM25Data)])
PM25Data <- PM25Data[, c(1:5, 12:15)]
PM25Data <- rename(PM25Data, pm2.5Marl = pm2.5, wsMarl = ws, wdMarl = wd, air_tempMarl
                  = air_temp)
PM25Data <- timeAverage(PM25Data, avg.time = "day", statistic = 'mean')

NO2Data <- subset(NO2Data, select = -c(wdKens, wdMarl))
COData <- subset(COData, select = -c(wdKens, wdMarl))
O3Data <- subset(O3Data, select = -c(wdKens, wdMarl))
SO2Data <- subset(SO2Data, select = -c(wdKens, wdMarl))
PM25Data <- subset(PM25Data, select = -c(wdKens, wdMarl))

allData <- bind_rows(kensData, marlData)

allData <- timeAverage(allData, time = 'day', statistic = 'mean')

yearlyAverage <- timeAverage(allData, avg.time = "year", statistic = 'mean')

allData$day <- lubridate::wday(allData$date, label = TRUE, abbr= FALSE, 
                               week_start = 1)

averageByDay <- allData %>%
  group_by(day) %>%
  summarise(across(co:air_temp, list(mean)))