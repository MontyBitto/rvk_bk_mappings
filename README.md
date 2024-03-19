# RVK_BK_Mappings
Dieses Programm soll ermitteln, welche RKV-Notationen nutzbare Mappings zur BK  in der Mapping-Registry von Cocoda haben. Dazu werden zunächst alle vorhanden RKV-BK Mappings geladen.

Danach wird die gesamte RVK mittels Abfragen an die coli-conc API rekursiv durchlaufen, und für jede Notation ermittelt, ob ein zur Anreicherung nutzbares Mapping existiert.

Die Ergebnisse werden zur Weiterverwendung lokal gespeichert.
