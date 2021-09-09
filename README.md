# Tnikify-Timeline-Map-Tool

this is a tool that help you filter events such as History or any events that you add to data folder in json format. Additionally, if there is a location specified, it will show the visual on map. For map, using the Leaflet library.

Note: in order for you to use, you will have to get an access token from https://www.mapbox.com/studio/account/tokens/ and replace in mapscript.js

# Technical details

* Program: Python

* Dependencies: python libraries and data folder

* python library: requirements.txt

# Screenshots

### basic view of how filter looks like
![screenshot1 - base look](https://raw.githubusercontent.com/NikhilTanni/tnikify-timeline-map-tool/main/screenshots/sc1.JPG)

### Themes changing
![screenshot2 - themes](https://raw.githubusercontent.com/NikhilTanni/tnikify-timeline-map-tool/main/screenshots/sc1.JPG)

### seek to year

double click on displayed year to open the prompt
![screenshot3 - input year](https://raw.githubusercontent.com/NikhilTanni/tnikify-timeline-map-tool/main/screenshots/sc1.JPG)

### draw line across pins on map

check the checkbox beside the locations to put a line (note: order of check matters)
![screenshot4 - line on map](https://raw.githubusercontent.com/NikhilTanni/tnikify-timeline-map-tool/main/screenshots/sc1.JPG)

### API response data - filter

use API paths to get filtered data

ex: http://<serverURL>/timeline/filter/time?start=1600-01&end=1700-01

Note that minimum yyyy-mm is mandatory then provide as much precision as you want in timestamp format: YYYY-MM-DDTh:i:s

![screenshot5 - API response data](https://raw.githubusercontent.com/NikhilTanni/tnikify-timeline-map-tool/main/screenshots/sc1.JPG)

# Contribution

Yes! data folder is in initial phase, please share the data!!

You can also develop the tool - enhance it, develop it. Aim is to use this for exploring and let hobbyist and curios people use it for their exploration.

# Current roadmap

1. logger and beautification
2. filter enhancements
3. UI range slider - include precision more than just year
4. Map calculation: angle between the points, distance between two points, etc
5. Timeline calculation: -TBD-
6. UI beautification
7. Integrate to tnikify-dashboard (not until this tool is in stable state)

priority wise: 1,2,4,3,6,5,7


# Notes

* This is still in devel phase, please don't use this anywhere in production or live environments

* The data folder content may or may not be fully correct.