library(openair)
library(tidyverse)
library(imputeTS)
library(corrplot)
library(sqldf)

# importing 2 datasets with the most complete data
marylData <- importAURN('MY1', year = 2015:2021)

kensData <- importAURN('KC1', year = 2015:2021)

# This code was needed as  different sources of data had a different amount of 
# rows in the dataset, the data was compared and and the missing rows were transferred
#In the end, i decided to use AURN source rather than the KCL as the data was 
# more complete
# kensDataNoNA <- drop_na(kensData)
# 
# kensData <- kensData[, -(16:18)]
# 
# kensData2 <- kensData2 %>% relocate(site, code, .before = date)
# 
# kensData2 <- kensData2[, -9]
# 
# kensData <- kensData[, -c(7, 12)]
# 
# kensData2 <- kensData2 %>% rename(pm2.5 = pm25)
# 
# diffRows <- sqldf('Select * from kensData where date not in (select date from kensData2)')
# 
# kensData2 <- rbind(kensData2, diffRows)

#plotting NA values and the distribution in the dataset
marylMissingO3 <- ggplot_na_distribution(marylData$o3, title = 'Missing O3 values - Marylebone Road')
marylMissingNO2 <- ggplot_na_distribution(marylData$no2, title = 'Missing NO2 values - Marylebone Road')
marylMissingPM10 <- ggplot_na_distribution(marylData$pm10, title = 'Missing PM10 values - Marylebone Road')
marylMissingPM25 <- ggplot_na_distribution(marylData$pm2.5, title = 'Missing PM2.5 values - Marylebone Road')

marylMissingO3
marylMissingNO2
marylMissingPM10
marylMissingPM25

kensMissingO3 <- ggplot_na_distribution(kensData$o3, title = 'Missing O3 values - N. Kensington')
kensMissingNO2 <- ggplot_na_distribution(kensData$no2, title = 'Missing NO2 values - N. Kensington')
kensMissingPM10 <- ggplot_na_distribution(kensData$pm10, title = 'Missing PM10 values - N. Kensington')
kensMissingPM25 <- ggplot_na_distribution(kensData$pm2.5, title = 'Missing PM2.5 values - N. Kensington')

kensMissingO3
kensMissingNO2
kensMissingPM10
kensMissingPM25

# keeping columns that are referenced on the LondonAir website that are stated
# to have an affect on health https://www.londonair.org.uk/LondonAir/nowcast.aspx
kensDataMain <- kensData[, c(1:3, 6, 7, 10)]

# dropping NA values so correlation matrix can be created
kensDataNoNA <- drop_na(kensDataMain)
dataCorrelation <- cor(kensDataNoNA[, 4:6])

corrplot(dataCorrelation)

# Amelia II uses means and variances to impute missing data, assumes data is 
# missing at random; and variables have multivariate normal distribution
library(Amelia)

kensDataOnly <- kensDataMain[, 3:6]
kensDataOnly <- as.data.frame(kensDataOnly)
# setting boundaries for imputation, variables cannot be negative
bound <- matrix(c(3, 2, 0, 0, Inf, Inf), nrow = 2, ncol = 3)
# Amelia function to impute data, m = number of datasets to create
kensDataAmelia <- amelia(kensDataOnly, m = 1, bounds = bound, max.resample = 10000)
kensDataImpute <- kensDataAmelia$imputations$imp1

# plotting the imputed values with the original dataset
kensDataO3Imp <- ggplot_na_imputations(kensData$o3, kensDataImpute$o3)
kensDataNO2Imp <- ggplot_na_imputations(kensData$no2, kensDataImpute$no2)
kensDataPM25Imp <- ggplot_na_imputations(kensData$pm2.5, kensDataImpute$pm2.5)

kensDataO3Imp
kensDataNO2Imp
kensDataPM25Imp

kensDataFinal <- kensDataImpute

# condensing hourly data to daily, for ease of use and faster processing
kensDataDaily <- timeAverage(kensDataFinal, avg.time = "day", statistic = 'mean')

kensDailyPlot <- ggplot(data = kensDataDaily, aes(x=date, y=value)) +
  geom_line(aes(y = no2, colour = 'red')) +
  geom_line(aes(y = o3, colour = 'blue')) +
  geom_line(aes(y = pm2.5, colour = 'green'))

kensDailyPlot2 <- ggplot(data = kensDataDaily, aes(x=date, y=value)) +
  geom_smooth(aes(y = no2, colour = 'red')) +
  geom_smooth(aes(y = o3, colour = 'blue')) +
  geom_smooth(aes(y = pm2.5, colour = 'green'))

kensDailyPlot
kensDailyPlot2
