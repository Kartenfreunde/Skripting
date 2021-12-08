# Welcome 

This is the German Amateur Astronomer Association's (www.sternfreunde.de) map project. We want to create an interactive map for anyone interested in places of astronomical interest (POAI). Intended features of the map:

* Shows places and areas, data collected and automatically updated from different sources
* Filter function to (de-)select certain categories (e.g. observatories, planetariums, dark sky areas …)
* Switchable overlays:
  * Light pollution
  * Terrain data
* Search field for addresses and locations 
* Embedable on any website like a widget (e.g. for astronomy clubs or media)

The coding is done in this repository named "scripting". The results of the scripts are then collected in the repository "[database](https://github.com/astronomieatlas-deutschland/database)"

# Scripting
The scripts will collect data from different sources (see "[Datenquellen](https://github.com/astronomieatlas-deutschland/scripting/blob/main/Datenquellen.ods)"). Which data sources can be summarized depends on the meta data that shall be shown for entries from certain categories.

1. First we start with [planetariums](https://github.com/astronomieatlas-deutschland/scripting/blob/main/AstronomyDatabaseWriter/astrodbwriter/crawler/gdp.py). 

The project is driven by a German-speaking group at the moment - but we are open for cooperation with anyone interested. Preparations, however, have been done in German: Zu vorbereitenden Überlegungen siehe https://etherpad.wikimedia.org/p/VdS-FG-AV_Karten-Kickoff-Besprechung-2021-02-04
