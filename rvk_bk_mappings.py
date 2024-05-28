import requests
import argparse
import csv

def get_other_direction(mapping_data):
 notation = args.notation
 if notation is None:
  notation = ""
 rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&limit=10000')
 rk_data = rk.json()
 for item in rk_data:
  try: #Einige RVK-BK Mappings haben keine BK Notation um zu zeigen, dass kein Mapping möglich ist.
   has_mapping = item["to"]['memberSet'][0]['notation'][0] #RVK und BK Notation sind umgedreht
   bk_notation = item["from"]['memberSet'][0]['notation'][0]
   relation = item["type"][0] #Relation zwischen den Notationen
   relation = relation.replace("http://www.w3.org/2004/02/skos/core#", "")
   if relation == "broadMatch": #da die Relationen umgedreht sind müssen broad und narrowMacht umgedreht werden
    relation = "narrowMatch"
   elif relation == "narrowMatch":
    relation = "broadMatch"
   mapping_uri = item['uri']
   if has_mapping.startswith(notation):
    mapping_data.append([has_mapping, bk_notation, relation, mapping_uri])
   if has_mapping in mapping_dict and has_mapping.startswith(notation): #Dictionary wird angelegt
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
 notation = args.notation
 if notation is None:
  notation = ""
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
   mapping_uri = item['uri']
   if notation is None or has_mapping.startswith(notation):
    mapping_data.append([has_mapping, bk_notation, relation, mapping_uri])
   if has_mapping in mapping_dict and has_mapping.startswith(notation): #Dictionary wird angelegt
    if bk_notation in mapping_dict[has_mapping]:
     mapping_dict[has_mapping][bk_notation].append(relation)
    else:
     mapping_dict[has_mapping][bk_notation] = [relation]
   else:
    mapping_dict[has_mapping] = {bk_notation: [relation]}
  except IndexError:
   pass
 mapping_data = get_other_direction(mapping_data)
 return mapping_data

def replace_characters(input_string): #RVK Notation für die API nutzbar machen
 replaced_string = input_string.replace(",", "%2C").replace(" ", "%2520")
 return replaced_string

def rvk_bk_process(rk_data, mapping_data):
 for item in rk_data: # Schleife durch die Konzepte
  notation = item['notation'][0] # nächst tiefere Notation
  if notation not in mapping_dict: # Notation hat noch kein Mapping
   mapping_data.append([notation])
  url_notation = replace_characters(notation)
  if url_notation:
   rvk_bk(url_notation, mapping_data) #Rekursion für alle Unterbegruppen
 return mapping_data

def rvk_bk(url_notation, mapping_data):
 print(url_notation)
 rk = requests.get('https://coli-conc.gbv.de/rvk/api/narrower?uri=http%3A%2F%2Frvk.uni-regensburg.de%2Fnt%2F'+url_notation) #Unterbegruppen
 rk_data = rk.json()
 rvk_bk_process(rk_data, mapping_data)

def start():
 mapping_data = get_current_mappings()
 if args.notation is None:
  rk = requests.get('https://coli-conc.gbv.de/api/voc/top?uri=http://uri.gbv.de/terminology/rvk/') #Hauptgruppen
 else: 
  notation = args.notation
  url_notation = replace_characters(notation)
  rk = requests.get('https://coli-conc.gbv.de/rvk/api/narrower?uri=http%3A%2F%2Frvk.uni-regensburg.de%2Fnt%2F'+ url_notation)
 rk_data = rk.json()
 rvk_bk_process(rk_data, mapping_data)
 return mapping_data

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--notation', dest="notation")
args = parser.parse_args()

mapping_data = start()
mapping_data.sort(key=lambda x: x[0])

with open('rvk_bk_mappings.tsv', mode='w', newline='', encoding='utf-8') as file:
 writer = csv.writer(file, delimiter='\t')
 writer.writerow(['has_mapping', 'bk_notation', 'relation', 'uri'])  # Header
 writer.writerows(mapping_data)
