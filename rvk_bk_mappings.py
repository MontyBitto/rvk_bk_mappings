import requests
import csv

def get_other_direction(mapping_data):
 rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&limit=10000')
 rk_data = rk.json()
 for item in rk_data:
  try: #Einige RVK-BK Mappings haben keine BK Notation um zu zeigen, dass kein Mapping möglich ist.
   has_mapping = item["to"]['memberSet'][0]['notation'][0]
   bk_notation = item["from"]['memberSet'][0]['notation'][0] #RVK Notation
   relation = item["type"][0] #Relation zwischen den Notationen
   relation = relation.replace("http://www.w3.org/2004/02/skos/core#", "")
   if relation == "broadMatch":
    relation = "narrowMatch"
   elif relation == "narrowMatch":
    relation = "broadMatch"
   mapping_data.append([has_mapping, bk_notation, relation])
   if has_mapping in mapping_dict: #Dictionary wird angelegt
    if bk_notation in mapping_dict[has_mapping]:
     mapping_dict[has_mapping][bk_notation].append(relation)
    else:
     mapping_dict[has_mapping][bk_notation] = [relation]
   else:
    mapping_dict[has_mapping] = {bk_notation: [relation]}
  except IndexError:
   pass
 return mapping_data

def get_current_mappings(): # Finde vorhandene Mappings, die Teil einer Konkordanz sind
 rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&partOf=any&limit=100000')
 rk_data = rk.json()
 global mapping_dict
 mapping_dict = {}
 mapping_data = []
 for item in rk_data:
  try: #Einige RVK-BK Mappings haben keine BK Notation um zu zeigen, dass kein Mapping möglich ist.
   bk_uri = item["to"]['memberSet'][0]['uri']
   has_mapping = item["from"]['memberSet'][0]['notation'][0] #RVK Notation
   bk_notation = bk_uri.replace("http://uri.gbv.de/terminology/bk/", "") #Da 2 Mappings kein notation Feld für BK haben wird die Notation über die URI ermittelt.
   relation = item["type"][0] #Relation zwischen den Notationen
   relation = relation.replace("http://www.w3.org/2004/02/skos/core#", "")
   mapping_data.append([has_mapping, bk_notation, relation])
   if has_mapping in mapping_dict: #Dictionary wird angelegt
    if bk_notation in mapping_dict[has_mapping]:
     mapping_dict[has_mapping][bk_notation].append(relation)
    else:
     mapping_dict[has_mapping][bk_notation] = [relation]
   else:
    mapping_dict[has_mapping] = {bk_notation: [relation]}
  except IndexError:
   pass
 mapping_data = get_other_direction(mapping_data)
 with open('rvk_bk_mapping_vorhanden.tsv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file, delimiter='\t')
  writer.writerow(['RVK Notation', 'BK Notation', 'Relation'])  # Header row
  writer.writerows(mapping_data)
 return

def replace_characters(input_string): #RVK Notation für die API nutzbar machen
 replaced_string = input_string.replace(",", "%2C").replace(" ", "%2520")
 return replaced_string

def rvk_bk_process(rk_data, no_mapping):
 for item in rk_data: # Schleife durch die Konzepte
  notation = item['notation'][0] # nächst tiefere Notation
  if notation not in mapping_dict: # Notation hat noch kein Mapping
   no_mapping.append(notation)
  else:
   for key, value in mapping_dict[notation].items(): #Nicht tiefer gehen wenn keine BK Untergruppe existiert und es ein narrow/exact Match ist
    if key in bk_narrowest and (value == "narrowMatch" or value == "exactMatch"):
     continue
  url_notation = replace_characters(notation)
  if url_notation:
   rvk_bk(url_notation, no_mapping) #Rekursion für alle Unterbegruppen
 return no_mapping

def rvk_bk(url_notation, no_mapping):
 rk = requests.get('https://coli-conc.gbv.de/api/concepts/narrower?uri=http://rvk.uni-regensburg.de/nt/'+url_notation) #Unterbegruppen
 rk_data = rk.json()
 rvk_bk_process(rk_data, no_mapping)

def start():
 no_mapping = []
 get_current_mappings()
 rk = requests.get('https://coli-conc.gbv.de/api/voc/top?uri=http://uri.gbv.de/terminology/rvk/') #Hauptgruppen
 rk_data = rk.json()
 rvk_bk_process(rk_data, no_mapping)
 return no_mapping

with open('narrowest.txt', 'r') as file: #Datei mit einer Liste der niedrigsten Untergruppen in der BK
 bk_narrowest = file.read()
no_mapping = start()
print("Fehlende mappings:", no_mapping)
print("Vorhandene mappings:", mapping_dict.keys())

with open("rvk_bk_kein_mapping.tsv", "w", newline='') as file:
 writer = csv.writer(file, delimiter='\t')
 writer.writerow(['RVK Notation'])
 for item in no_mapping:
  writer.writerow([item])
