library(openair)
library(tidyverse)
library(tsbox)
library(imputeTS)
library(ggmap)
library(ggrepel)
library(skimr)

# importing metadata, including latitude and longitude
metadata <- importMeta(source = "AURN")
metadataKCL <- importMeta(source = "kcl")
# creating london borders by looking at the sites one the edges of london and 
# taking positional data of those site, probably not the best method
londonMeta <- filter(metadata, metadata$longitude > -0.460861 & metadata$longitude < 0.184806)
londonMetaAll <- filter(londonMeta, londonMeta$latitude > 51.35866 & londonMeta$latitude < 51.66864)

metadataKCL <- filter(metadataKCL, metadataKCL$longitude > -0.460861 & metadataKCL$longitude < 0.184806)
metadataKCL <- filter(metadataKCL, metadataKCL$latitude > 51.35866 & metadata$latitude < 51.66864)

summary(metadataKCL)
summary(londonMetaAll)

# On the londonair website, some sites have been closed in the last decade however
# data for them will still be attempted to be imported resulting in errors. This
# list of will filter out the closed sites
closedSites <- read.csv('Data\\closedSites.csv')

londonMetaOpen <- filter(londonMetaAll, !(londonMetaAll$code %in% closedSites$ï..Sites))
metaKCLOpen <- filter(metadataKCL, !(metadataKCL$code %in% closedSites$ï..Sites))

# openair package allows data to be imported directly as R data objects, here I 
# am importing based on the site codes I have left after filtering, meta = true 
# means site type (area details) and positional data is included
londonData <- importAURN(londonMetaOpen$code, year = 2015:2021, pollutant = 
                           c("co", "no2", "so2", "pm2.5", "o3"),
                          verbose = TRUE, meta = TRUE)

londonKCLSites <- metaKCLOpen$code

londonDataKCL <- importKCL(site = londonKCLSites, year = 2015:2021, pollutant = 
                                      c("co", "no2", "so2", "pm25"))

NO2boxplot <- ggplot(londonDataAURN, aes(x = site_type, y = no2, color = site)) + 
  geom_boxplot(outlier.shape = NA) +
  coord_cartesian(ylim = c(0, 180)) +
  ggtitle("Distribution of NO2 values by site") +
  xlab("Site Type") + ylab("NO2 (µg/m3)")

MissingO3bySite <- londonDataAURN %>%
    group_by(site) %>%
    summarise(sum(is.na(o3)))

MissingO3bySite['percentMissing'] <- MissingO3bySite$`sum(is.na(o3))` / 61368
MissingO3bySite['valuesPresent'] <- 1 - MissingO3bySite$percentMissing  

missingO3Plot <- ggplot(MissingO3bySite, aes(x = percentMissing, y = site)) +
  geom_bar(stat = 'identity', fill = 'orange') + ggtitle("Missing O3 values by site") +
  scale_x_continuous(labels = scales::percent) +
  xlab("Proportion of Missing Values") + ylab("Site")

skimData <- skim(londonDataAURN)
summary(londonDataAURN)

missingO3Plot
NO2boxplot

sites <- unique(londonData$site)
sitesKCL <- unique(londonDataKCL$code)
longitude <- unique(londonData$longitude)
latitude <- unique(londonData$latitude)
latitude <- append(latitude, 51.52253, after = length(latitude))

siteLocation <- data.frame(sites, longitude, latitude)

londonDataFilter <- londonData[,c(1:4, 6, 8, 9, 11, 16:21)]

for (i in 1:17) {
  print(sites[i])
  siteFilter <- dplyr::filter(londonDataFilter, londonData$site == sites[i])
  print(summary(siteFilter))
}

for (i in 1:57) {
  print(sitesKCL[i])
  siteFilter <- dplyr::filter(londonDataKCL, londonDataKCL$code == sitesKCL[i])
  print(summary(siteFilter))
}

summary(londonData)

# google maps api to plot the locations of the sites in the dataset on to a map
# of London
londonMap = get_map(source = 'stamen', location = 'London', maptype = 'terrain-lines')

ggmap(londonMap)

ggmap(londonMap) + geom_point(aes(x = longitude, y = latitude),
                    data = siteLocation) + geom_text_repel(data = siteLocation, 
                    aes(x = longitude, y = latitude, label = sites), size = 3)
                    
# plotting a bar graph of proportion of missing data (not NA values, but timesteps
# that are missing)
missingDataGraph <- ggplot(londonData[,2], aes(x=code)) +
  geom_bar()
  
missingDataGraph

# filtering out the sites with incomplete dataset
missingCode <- c('BDMP', 'HP1', 'HR3', 'TED')

londonDataFilter <- filter(londonData, !(code %in% missingCode))

summary(londonDataFilter)

sites <- unique(londonDataFilter$site)

# printing a summary for each site which includes NA values for each variable
for (i in 1:13) {
  print(sites[i])
  siteFilter <- filter(londonDataFilter, londonDataFilter$site == sites[i])
  print(summary(siteFilter))
}