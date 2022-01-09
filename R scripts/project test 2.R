library(openair)
library(tidyverse)
library(tsbox)
library(imputeTS)
library(ggmap)
library(ggrepel)

metadata <- importMeta(source = "AURN")
londonMeta <- filter(metadata, metadata$longitude > -0.460861 & metadata$longitude < 0.184806)
londonMetaAll <- filter(londonMeta, londonMeta$latitude > 51.35866 & londonMeta$latitude < 51.66864)

summary(londonMetaAll)

closedSites <- read.csv('C:\\Users\\yadlo\\Desktop\\Year 3\\Project\\Data\\closedSites.csv')

londonMetaOpen <- filter(londonMetaAll, !(londonMetaAll$code %in% closedSites$ï..Sites))

londonMetaOpen$code

londonData <- importAURN(londonMetaOpen$code, year = 2015:2021,
                          verbose = TRUE, meta = TRUE)

boxplot <- ggplot(londonData, aes(x = site_type, y = pm10, color = site_type)) + geom_boxplot()

sites <- unique(londonData$site)
longitude <- unique(londonData$longitude)
latitude <- unique(londonData$latitude)
latitude <- append(latitude, 51.52253, after = length(latitude))

siteLocation <- data.frame(sites, longitude, latitude)

for (i in 1:17) {
  print(sites[i])
  siteFilter <- filter(londonData, londonData$site == sites[i])
  print(summary(siteFilter))
}

summary(londonData)

cor(londonData[4:17],)

londonMap = get_map(source = 'stamen', location = 'London', maptype = 'terrain-lines')

ggmap(londonMap)

ggmap(londonMap) + geom_point(aes(x = longitude, y = latitude),
                    data = siteLocation) + geom_text_repel(data = siteLocation, 
                    aes(x = longitude, y = latitude, label = sites), size = 3)
