import requests

def get_other_direction(mapping_data):
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
   mapping_data.append([has_mapping, bk_notation, relation, mapping_uri])
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
   mapping_uri = item['uri']
   mapping_data.append([has_mapping, bk_notation, relation, mapping_uri])
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
 return mapping_data



mapping_data = get_current_mappings()
mapping_data.sort(key=lambda x: x[0])

uniquervk = []
uniquebk = []
with open('rvk_bk.pg', mode='w', encoding='utf-8') as file:
 for item in mapping_data:
  if item[0] not in uniquervk:
   file.write(f"\"{item[0]}\" :rvk notaion:\"{item[0]}\"\n")
   uniquervk.append(item[0])
  if item[1] not in uniquebk:
   file.write(f"\"{item[1]}\" :bk notation:\"{item[1]}\"\n")
   uniquebk.append(item[1])
  file.write(f"\"{item[0]}\" -> \"{item[1]}\" relation:\"{item[2]}\" uri:\"{item[3]}\"\n")
