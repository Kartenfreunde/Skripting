## Open questions / Zu klären

1. How should the data/UI be hosted? Stefan offers webspace/-server, if needed.
1. How many separate tables for categories do we need? --> see https://github.com/astronomieatlas-deutschland/Skripting/issues/1
1. How do we make sure that no duplicates are created when parsing data automatically from different sources? (Wie stellen wir sicher, dass bei automatischen Aktualisierungen und Datenabruf aus mehreren Quellen keine Duplikate auftreten?)
1. We have to clarify what copyrights can be held on geographic metadata, i.e. how much geographic data we can copy from different sources. Daniel asks a friend about the law situation. Law information to OpenStreetMap: https://wiki.openstreetmap.org/wiki/Using_OpenStreetMap

## results from / Ergebnisse vom 27.10.2021

Michael reports that the VdS is creating a new information brochure with a map on the back showing all VdS member observatories / clubs. It would be great to have a draft map until end of the year. Fabian helps at least with getting the coordinates of the observatories and maybe also with creating the map.

Benjamin stays in contact with the Gesellschaft für Chronometrie e. V. regarding the questions about sundials and talks with Olaf Kretzer about astronomical places in Thüringen.

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

## results from / Ergebnisse vom 30.08.2021

- Vorstellung Stand aus Technikgruppe und, wie github-Repository funktioniert. Technik/Hosting --> Micha lädt Gerrit G. zum nächsten Treffen ein, 
- Frage nach Internationalität des Projekts: Gruppe ist sehr offen für Mitarbeit über Ländergrenzen hinweg, Kontakte insbes. über Planetarium Society und IAU möglich.
- Astrotreff: Benjamin fragt bei Matthias (Caros Kontakt)
- astrospots.com : Micha fühlt mal vor, ob Zusammenarbeit gewünscht
- Nächste Termine: 29.9. Technikrunde / 13.10. große Runde
