# RVK-BK

## Dependencies
- pip install requests
- https://github.com/pg-format/pgraphs/
- bk__default.jskos.ndjson von https://api.dante.gbv.de/export/download/bk/default/
- rvko_xml.zip von https://rvk.uni-regensburg.de/regensburger-verbundklassifikation-online/rvk-download
- kxp-subjects.tsv.gz von https://doi.org/10.5281/zenodo.7016625

## Nutzung
### Erstelle .pg und .csv Dateien
rvko_xml.zip, bk__default.jskos.ndjson und kxp-subjects.pg müssen in diesem Ordner liegen.  
pgraphs muss wie in https://github.com/pg-format/pgraphs/ beschrieben installiert sein. 
Mit `make` wird ein Property-Graph mit erstellt und daraus CSV-Dateien. Das erste mal kann dies ein paar Minuten dauern, da kxp-subjects sehr groß ist.  
In some some_subjects.pg und den daraus entstandenen CSV-Dateien sind nur die ersten 4000000 Zeilen aus kxp-subjects.pg, da pgraphs nicht mit größeren Dateien umgehen kann. 

### Führe die Dateien in Neo4j
Erstelle neo4j/import in pgraphs und verschiebe die CSV-Dateien in den Ordner.  
Mit `./import.sh subjects` in pgraphs/neo4j wird ein Neo4j docker erstellt mit den Inhalten der CSV-Dateien. Neo4j ist unter http://localhost:7474/browser/ zu finden, Username und Password müssen leer sein beim verbinden.