# RVK-BK

## Dependencies
- pip install requests
- https://github.com/pg-format/pgraphs/

## Nutzung
### Erstelle .pg und .csv Dateien
pgraphs muss wie in `https://github.com/pg-format/pgraphs/` beschrieben installiert sein. 
Mit `make` wird ein Property-Graph mit erstellt und daraus CSV-Dateien. Das erste mal kann dies ein paar Minuten dauern, da kxp-subjects sehr groß ist.  
In some `some_subjects.pg` und den daraus entstandenen CSV-Dateien sind nur die ersten 4000000 Zeilen aus `kxp-subjects.pg`, da pgraphs nicht mit größeren Dateien umgehen kann. 

### Führe die Dateien in Neo4j
Erstelle `neo4j/import` in `pgraphs` und verschiebe die CSV-Dateien in den Ordner.  
Mit `./import.sh subjects` in `pgraphs/neo4j` wird ein Neo4j docker erstellt mit den Inhalten der CSV-Dateien. Neo4j ist unter `http://localhost:7474/browser/` zu finden, Username und Password müssen beim verbinden leer sein.

### Nutzen des Graphen

In dem Graph sind Sachgebiete von der PPN auf die Notation gerichtet.

Durch Cypher Befehle kann man in Neo4j jetzt Informationen erhalten. Z. B. welche RVK-Notationen haben ein “exactMatch” oder “narrowMatch” mit BK-Notationen, die mit PPNs verbunden werden können `MATCH p=((r:rvk)-[m]->(b:bk)<-[]-(t:title)) WHERE m.relation = 'exactMatch' or m.relation = 'narrowMatch' RETURN p`. Mit so einer Frage ließen sich PPNs finden, die noch mit RVK angereichert werden können.

`MATCH (b:bk) RETURN b und MATCH (r:rvk) RETURN r` geben jeweils die komplette Klassifikation und ihre Hierarchie zurück.


Mit `MATCH p=(t:title)-[]->() WHERE t.ppn = "010000844" RETURN p` lassen sich alle Sachgebiete einer bestimmten PPN ausgeben, in diesem Fall 010000844.

Andersrum lässt sich mit `MATCH p=()-[r:subject]->(r:rvk) WHERE r.notation = "MS 2870" RETURN p` finden, wie viel ein Sachgebiet in K10plus genutzt wird.

Mit `MATCH p=((r:rvk)-[]->(b:bk)) WHERE b.notation = "17.03" RETURN p` lassen sich alle Mappings eine Notation anzeigen.

CYPHER queries for each query type:

occurrences:   
`MATCH (t:title)-[]->(n:?) WHERE n.notation = "?" RETURN count(t) AS freq`  

coOccurrences:  
`MATCH (t:title)-[]->(n:?) WHERE n.notation = "?" MATCH (t)-[]->(m:?) RETURN head(LABELS(m)), m.notation, count(m) AS freq`

subjects:  
`MATCH (t:title)-[]->(n) WHERE t.ppn = "?" RETURN head(LABELS(n)), n.notation`   

records:  
`MATCH (t:title)-[]->(n:?) WHERE n.notation = "?" RETURN t.ppn LIMIT ?`  

CYPHER queries with their respective sample query:

occurrences of RVK DG 9000  
`MATCH (t:title)-[]->(r:rvk) WHERE r.notation = "DG 9000" RETURN count(t)`

co-occurrences of RVK DG 9000 in BK  
`MATCH (t:title)-[]->(r:rvk) WHERE r.notation = "DG 9000" MATCH (t)-[]->(b:bk) RETURN head(LABELS(b)), b.notation, count(b)`

co-occurrences of RVK DG 9000 in all vocabularies  
`MATCH (t:title)-[]->(r:rvk) WHERE r.notation = "DG 9000" MATCH (t)-[]->(n) WHERE not LABELS(n) = ["rvk"] RETURN head(LABELS(n)), n.notation, count(n)`

co-occurrences of RVK DG 9000 in all vocabularies (including RVK)  
`MATCH (t:title)-[]->(r:rvk) WHERE r.notation = "DG 9000" MATCH (t)-[]->(n) RETURN head(LABELS(n)), n.notation, count(n)`

subjects of a record (all vocabularies)  
`MATCH (t:title)-[]->(n) WHERE t.ppn = "012401471" RETURN head(LABELS(n)), n.notation`

subjects of a record (selected vocabulary)  
`MATCH (t:title)-[]->(r:rvk) WHERE t.ppn = "012401471" RETURN head(LABELS(r)), r.notation`

records of a subject  
`MATCH (t:title)-[]->(b:bk) WHERE b.notation = "20.04" RETURN t.ppn`