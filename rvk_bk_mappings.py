import requests
import argparse
import csv

def process_item(item, reverse_relation):
    global mapping_dict
    try:
        if reverse_relation:
            has_mapping = item["to"]['memberSet'][0]['notation'][0]  # RVK und BK Notation sind umgedreht
            bk_notation = item["from"]['memberSet'][0]['notation'][0]
        else:
            bk_uri = item["to"]['memberSet'][0]['uri']
            has_mapping = item["from"]['memberSet'][0]['notation'][0]  # RVK Notation
            bk_notation = bk_uri.replace("http://uri.gbv.de/terminology/bk/", "")  # Da 2 Mappings kein notation Feld für BK haben wird die Notation über die URI ermittelt.

        relation = item["type"][0]  # Relation zwischen den Notationen
        relation = relation.replace("http://www.w3.org/2004/02/skos/core#", "")
        if reverse_relation and relation == "broadMatch":  # Da die Relationen umgedreht sind müssen broad und narrowMacht umgedreht werden
            relation = "narrowMatch"
        mapping_uri = item['uri']
        skip = False
        for anno in item["annotations"]: # Mappings mit minus Bewertungen werden nicht beachtet.
            try: # Es existieren auch annotations, die das mapping confirmen. Diese werden ignoriert.
                if anno["bodyValue"] == "-1":
                    skip = True
            except (KeyError):
                pass
        if skip:
            return
        if has_mapping in mapping_dict:  # Dictionary wird angelegt
            if bk_notation in mapping_dict[has_mapping]:
                mapping_dict[has_mapping][bk_notation].append([relation, mapping_uri])
            else:
                mapping_dict[has_mapping][bk_notation] = [[relation, mapping_uri]]
        else:
            mapping_dict[has_mapping] = {bk_notation: [[relation, mapping_uri]]}
    except (IndexError):
        pass
    return

def get_other_direction():
    rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&limit=10000&type=http%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23exactMatch|http%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23broadMatch&properties=annotations')
    rk_data = rk.json()
    for item in rk_data:
        process_item(item, reverse_relation=True)
    return

def get_current_mappings():  # Finde vorhandene Mappings, die Teil einer Konkordanz sind
    rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&partOf=any&limit=100000&type=http%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23exactMatch|http%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23narrowMatch&properties=annotations')
    rk_data = rk.json()
    global mapping_dict
    mapping_dict = {}
    for item in rk_data:
        process_item(item, reverse_relation=False)
    get_other_direction()
    return



def replace_characters(input_string): #RVK Notation für die API nutzbar machen
  replaced_string = input_string.replace(",", "%2C").replace(" ", "%2520")
  return replaced_string

def rvk_bk_process(rk_data, mapping_data, stack, level, broader):
  for item in rk_data: # Schleife durch die Konzepte
    notation = item['notation'][0] # nächst tiefere Notation
    if "http://rdf-vocabulary.ddialliance.org/xkos#CombinedConcept" in item["type"]:
      type = "combined"
    else:
      type = ""

    temp = []
    if (stack == [] or stack[-1] == []) and notation not in mapping_dict: # Notation hat noch kein Mapping
      mapping_data.append([level, notation, type, "", "", "", "", broader])

    if notation in mapping_dict: # Notation hat ein Mapping
      for bk_not, bk in mapping_dict[notation].items():
        bk_notation = bk_not         
        for relation_mapping in bk:
          relation = relation_mapping[0]
          mapping_uri = relation_mapping[1]
          mapping_data.append([level, notation, type, "", bk_notation, relation, mapping_uri, broader])
          if bk_notation in bk_narrowest: #Wenn die BK Notation auf dem niedrigsten level ist wird das Mapping auch für die niedrigeren RVK Notationen "indirekt" verwendet.
            temp.append(["yes", bk_notation, relation, mapping_uri])
    if stack:
      for sta in stack[-1]:
        if sta not in temp:
          mapping_data.append([level, notation, type, sta[0], sta[1], sta[2], sta[3], broader])
          temp.append(sta)
    stack.append(temp)
    url_notation = replace_characters(notation)
    if url_notation:
      rvk_bk(url_notation, mapping_data, stack, level +1, notation) #Rekursion für alle Unterbegruppen
    if stack:
      stack.pop()
  return mapping_data

def rvk_bk(url_notation, mapping_data, stack, level, broader):
  rk = requests.get('https://coli-conc.gbv.de/rvk/api/narrower?uri=http%3A%2F%2Frvk.uni-regensburg.de%2Fnt%2F'+url_notation) #Unterbegruppen
  rk_data = rk.json()
  rk_data = sorted(rk_data, key=lambda x: x['notation'][0]) # Spätere sortierung würde z. B. UB 1070 - UB 1107 nach UB 1070 haben. Später wäre mit RegEx möglich.

  rvk_bk_process(rk_data, mapping_data, stack, level, broader)

def start():
  if args.dry: #Nur die RVK Notationen
    global mapping_dict
    mapping_dict = {}
  else:
    get_current_mappings()
  mapping_data = []
  if args.notation is None: # Starte am Anfang
    notation = ""
    rk = requests.get('https://coli-conc.gbv.de/api/voc/top?uri=http://uri.gbv.de/terminology/rvk/') #Hauptgruppen
  else: # Starte bei der eingegeben Notation (nicht einschliesslich)
    notation = args.notation
    url_notation = replace_characters(notation)
    rk = requests.get('https://coli-conc.gbv.de/rvk/api/narrower?uri=http%3A%2F%2Frvk.uni-regensburg.de%2Fnt%2F'+ url_notation)
  rk_data = rk.json()
  rk_data = sorted(rk_data, key=lambda x: x['notation'][0])
  rvk_bk_process(rk_data, mapping_data, [], 0, notation)
  return mapping_data

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--notation', dest="notation")
parser.add_argument('-d', '--dry', dest="dry", action='store_true')

args = parser.parse_args()

with open('bk_narrowest.csv', 'r') as file: #Datei mit einer Liste der niedrigsten Untergruppen in der BK
  bk_narrowest = file.read()

  mapping_data = start()

with open('rvk_bk_mappings.tsv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file, delimiter='\t')
  writer.writerow(['Level', 'RVK Notation', 'Notation Type', 'indirekt', 'BK Notation', 'Relation Type', 'URI', 'Broader Notation'])  # Header
  writer.writerows(mapping_data)