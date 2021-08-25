## Open questions / Zu klären

1. How should the data/UI be hosted? Stefan offers webspace/-server, if needed.
1. How many separate tables for categories do we need?
1. Wie stellen wir sicher, dass bei automatischen Aktualisierungen und Datenabruf aus mehreren Quellen keine Duplikate auftreten?

## results from / Ergebnisse vom 25.08.2021

### Kurze Github-Einführung ✅ - 
see https://docs.github.com

### Wollen wir das Projekt potentiell international nutzbar aufziehen
Thomas, Stefan und Benjamin meinen Ja. Somit hier auch EN oder multilingual kommunizieren?
User Interface should be multilingual; we'll have to develop a system which can handle translations.
--> Stefan: www.deepl.com nutzen?

### Wie soll die Datenbank am Schluss aussehen (Dateistruktur, Datenfelder)? Thomas legt schon mal was an.
Thomas has created a structure with possible fields for planetaria: https://github.com/astronomieatlas-deutschland/Skripting/blob/main/AstronomyDatabaseWriter/astrodbwriter/category/planetarium.py
How to identify if a place belongs to more than one category? --> We'll add a field "category", if necessary. We'll use Python's inherit functions to join data. 

### Wer möchte wie mit dem Skripting loslegen?
--> @Fabian, do you already have something ready? Then feel free to commit...

### Starten mit einem Ablaufplan 
we use the bugtracker/issues section in this Github repository: https://github.com/astronomieatlas-deutschland/Skripting/issues
