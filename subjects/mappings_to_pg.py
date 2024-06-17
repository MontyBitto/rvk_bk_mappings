import requests
import argparse

def process_item(mapping_data, item):
  try:
    to_uri = item["to"]['memberSet'][0]['uri'].replace("%2C", ",").replace("%20", " ")
    from_uri = item["from"]['memberSet'][0]['uri'].replace("%2C", ",").replace("%20", " ")

      
    relation = item["type"][0]  # Relation zwischen den Notationen
    relation = relation.replace("http://www.w3.org/2004/02/skos/core#", "")
    mapping_uri = item['uri']
    mapping_data.append([from_uri, to_uri, relation, mapping_uri])
  except (IndexError):
    pass
  return mapping_data

def fetch_mappings(from_scheme, to_scheme):
    url = f'https://coli-conc.gbv.de/api/mappings?fromScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F{from_scheme}&toScheme=http%3A%2F%2Fbartoc.org%2Fen%2Fnode%2F{to_scheme}&limit=500000&direction=both&cardinality=1-to-1'
    response = requests.get(url)
    return response.json()

def get_all_mappings(schemes):
    mapping_data = []
    for from_scheme in schemes:
        for to_scheme in schemes:
            if from_scheme != to_scheme:
                response = fetch_mappings(from_scheme, to_scheme)
                for item in response:
                    process_item(mapping_data, item)
    return mapping_data

def parse_schemes(input_str):
    schemes = input_str.split(',')
    return schemes

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--schemes', type=str, required=True, help="Comma-separated list of BARTOC nodes")
args = parser.parse_args()
schemes = parse_schemes(args.schemes)
if len(schemes) < 2:
  raise ValueError("At least two schemes are required.")
mapping_data = get_all_mappings(schemes)

for item in mapping_data:
  print(f"\"{item[0]}\" -> \"{item[1]}\" :mapping relation:\"{item[2]}\" uri:\"{item[3]}\"")
