import requests

def get_current_mappings(): # Finde vorhandene Mappings, die Teil einer Konkordanz sind
 rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&partOf=any&limit=100000')
 rk_data = rk.json()
 global mapping_dict
 mapping_dict = {}
 no_possible_mapping = []
 for item in rk_data:
  try:
   bk_uri = item["to"]['memberSet'][0]['uri']
   bk_notation = bk_uri.replace("http://uri.gbv.de/terminology/bk/", "")
   has_mapping = item["from"]['memberSet'][0]['notation'][0]
   relation = item["type"][0]
   if has_mapping in mapping_dict:
    if bk_notation in mapping_dict[has_mapping]:
     mapping_dict[has_mapping][bk_notation].append(relation)
    else:
     mapping_dict[has_mapping][bk_notation] = [relation]
   else:
    mapping_dict[has_mapping] = {bk_notation: [relation]}
  except IndexError:
   no_possible_mapping.append(item["from"]['memberSet'][0]['notation'][0])
 return

def replace_characters(input_string): #RVK Notation für die API nutzbar machen
 replaced_string = input_string.replace(",", "%2C").replace(" ", "%2520")
 return replaced_string

def rvk_bk_process(rk_data, no_mapping):
 for item in rk_data: # Schleife durch die Konzepte
  notation = item['notation'][0] # z.B. "AV"
  if notation not in mapping_dict: # Notation hat noch kein Mapping
   no_mapping.append(notation)
  else:
   for key, value in mapping_dict[notation].items():
    if key in bk_narrowest and (value == "http://www.w3.org/2004/02/skos/core#narrowMatch" or value == "http://www.w3.org/2004/02/skos/core#exactMatch"): #wenn keine BK Untergruppe und narrow/exact Match
     continue
  url_notation = replace_characters(notation)
  if url_notation:
   rvk_bk(url_notation, no_mapping) #Rekursion für alle Unterbegruppen
 return no_mapping

def rvk_bk(url_notation, no_mapping): #url_notation = z.B. "A"
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

with open('narrowest.txt', 'r') as file:
    bk_narrowest = file.read()
no_mapping = start()
print("Fehlende mappings:", no_mapping)
print("Vorhandene mappings:", mapping_dict.keys())

with open("rvk_bk_mapping_vorhanden.txt", "w") as file:
    file.write("Has mapping: {}\n".format(mapping_dict.keys()))
with open("rvk_bk_kein_mapping.txt", "w") as file:
    file.write("No mapping: {}\n".format(no_mapping))
