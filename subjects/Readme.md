# RVK-BK

## Dependencies
- pip install requests
- https://github.com/pg-format/pgraphs/
- kxp-subjects.tsv.gz von https://doi.org/10.5281/zenodo.7016625

## Nutzung
### Erstelle .pg und .csv Dateien
`rvko_xml.zip`, `bk__default.jskos.ndjson` und `kxp-subjects.pg` müssen in diesem Ordner liegen.  
pgraphs muss wie in `https://github.com/pg-format/pgraphs/` beschrieben installiert sein. 
Mit `make` wird ein Property-Graph mit erstellt und daraus CSV-Dateien. Das erste mal kann dies ein paar Minuten dauern, da kxp-subjects sehr groß ist.  
In some `some_subjects.pg` und den daraus entstandenen CSV-Dateien sind nur die ersten 4000000 Zeilen aus `kxp-subjects.pg`, da pgraphs nicht mit größeren Dateien umgehen kann. 

### Führe die Dateien in Neo4j
Erstelle `neo4j/import` in `pgraphs` und verschiebe die CSV-Dateien in den Ordner.  
Mit `./import.sh subjects` in `pgraphs/neo4j` wird ein Neo4j docker erstellt mit den Inhalten der CSV-Dateien. Neo4j ist unter `http://localhost:7474/browser/` zu finden, Username und Password müssen beim verbinden leer sein.

### Nutzen des Graphen

In dem Graph sind Mappings immer von RVK auf BK gerichtet und Sachgebiete von der PPN auf die Notation gerichtet.

Durch Cypher Befehle kann man in Neo4j jetzt Informationen erhalten. Z. B. welche RVK-Notationen haben ein “exactMatch” oder “narrowMatch” mit BK-Notationen, die mit PPNs verbunden werden können `MATCH p=((r:rvk)-[m]->(b:bk)<-[]-(t:title)) WHERE m.relation = 'exactMatch' or m.relation = 'narrowMatch' RETURN p`. Mit so einer Frage ließen sich PPNs finden, die noch mit RVK angereichert werden können.

`MATCH (b:bk) RETURN b und MATCH (r:rvk) RETURN r` geben jeweils die komplette Klassifikation und ihre Hierarchie zurück.


`Mit MATCH p=(t:title)-[]->() WHERE t.ppn = "010000844" RETURN p` lassen sich alle Sachgebiete einer bestimmten PPN ausgeben, in diesem Fall 010000844.

Andersrum lässt sich mit `MATCH p=()-[r:subject]->(r:rvk) WHERE r.notation = "MS 2870" RETURN p` finden, wie viel ein Sachgebiet in K10plus genutzt wird.

`Mit MATCH p=((r:rvk)-[]->(b:bk)) WHERE b.notation = "17.03" RETURN p` lassen sich alle Mappings eine Notation anzeigen.
