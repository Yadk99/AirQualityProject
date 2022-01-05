library(openair)
library(tidyverse)
library(tsbox)


metadata <- importMeta(source = "AURN")
londonMeta <- filter(metadata, metadata$longitude > -0.460861 & metadata$longitude < 0.184806)
londonMetaAll <- filter(londonMeta, londonMeta$latitude > 51.35866 & londonMeta$latitude < 51.66864)

summary(londonMetaAll)

closedSites <- read.csv('C:\\Users\\yadlo\\Desktop\\Year 3\\Project\\closedSites.csv')

londonMetaOpen <- filter(londonMetaAll, !(londonMetaAll$code %in% closedSites$ï..Sites))

londonSample <- sample_n(londonMetaOpen, 3)

sampleData <- importAURN(londonSample$code, year = 2015:2020, data_type = "daily")

londonMetaOpen$code

londonData <- importAURN(londonMetaOpen$code, year = 2015:2020,
                          verbose = TRUE, meta = TRUE)

boxplot <- ggplot(londonData, aes(x = site_type, y = pm10, color = site_type)) + geom_boxplot()

boxplot

londonDataomit <- londonData %>%
  na.omit()

londonDataSites <- londonData %>%
  group_by()

unique(londonData$site)

londonFilter <- londonData[londonData$site=="London Westminster",]
summary(londonFilter)

londonFilter$date <- ts_ts(londonFilter$date)