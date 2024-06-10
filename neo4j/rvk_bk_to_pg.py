import requests

def process_item(mapping_data, item, reverse_relation):
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
    elif reverse_relation and relation == "narrowMatch":
      print(1)
      relation = "broadMatch"
    mapping_uri = item['uri']
    mapping_data.append([has_mapping, bk_notation, relation, mapping_uri])
  except (IndexError):
    pass
  return mapping_data

def get_other_direction(mapping_data):
  rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&limit=10000')
  rk_data = rk.json()
  for item in rk_data:
    process_item(mapping_data, item, reverse_relation=True)
  return mapping_data

def get_current_mappings(): # Finde vorhandene Mappings, die Teil einer Konkordanz sind
  rk = requests.get('https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F533&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F18785&partOf=any&limit=100000')
  rk_data = rk.json()
  mapping_data = []
  for item in rk_data:
    process_item(mapping_data, item, reverse_relation=False)
  mapping_data = get_other_direction(mapping_data)
  return mapping_data

mapping_data = get_current_mappings()
mapping_data.sort(key=lambda x: x[0])

for item in mapping_data:
  print(f"\"{item[0]}\" -> \"{item[1]}\" :mapping relation:\"{item[2]}\" uri:\"{item[3]}\"")