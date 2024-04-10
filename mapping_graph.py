import requests
import plotly.graph_objects as go
import numpy as np

rk = requests.get('https://coli-conc.gbv.de/api/mappings?limit=100000000')
rk_data = rk.json()

count_dict = {}

for item in rk_data:
    from_uri = item['fromScheme']['uri']
    to_uri = item['toScheme']['uri']
    
    mapping_key = (from_uri, to_uri)
    count_dict[mapping_key] = count_dict.get(mapping_key, 0) + 1

count_mappings = [
    {"from": key[0], "to": key[1], "weight": value}
    for key, value in count_dict.items()
]

uri_to_not = {'http://bartoc.org/en/node/20407': 'thuana',
 'http://bartoc.org/en/node/1324': 'SEB',
 'http://bartoc.org/en/node/1042': 'FOS',
 'http://bartoc.org/en/node/20404': 'retrohab',
 'http://bartoc.org/en/node/430': 'GND',
 'http://bartoc.org/en/node/18785': 'BK',
 'http://bartoc.org/en/node/241': 'DDC',
 'http://bartoc.org/en/node/533': 'RVK',
 'http://bartoc.org/en/node/1707': 'ULBB',
 'http://bartoc.org/en/node/20430': 'OBV',
 'http://bartoc.org/en/node/18797': 'IxTheo',
 'http://bartoc.org/en/node/20049': 'SDNB',
 'http://bartoc.org/en/node/1443': 'KonSys',
 'http://bartoc.org/en/node/1940': 'WD',
 'http://bartoc.org/en/node/75': 'AAT',
 'http://bartoc.org/en/node/1665': 'nkostype',
 'http://bartoc.org/en/node/1094': 'ÖFOS',
 'http://bartoc.org/en/node/520': 'DFG',
 'http://bartoc.org/en/node/18497': 'DNBSGR',
 'http://uri.gbv.de/terminology/bk/': 'BK',
 'http://bartoc.org/en/node/20405': 'gessner',
 'http://bartoc.org/en/node/20406': 'brunfels',
 'http://uri.gbv.de/terminology/rvk/': 'RVK',
 'http://bartoc.org/en/node/20298': 'NSK',
 'http://bartoc.org/en/node/20400': 'BC',
 'http://zbw.eu/stw': 'STW',
 'http://bartoc.org/en/node/1043': 'thema',
 'http://id.nlm.nih.gov/mesh': 'MeSH',
 'http://id.loc.gov/authorities/subjects': 'LCSH',
 'http://dewey.info/scheme/edition/e23/': 'DDC',
 'http://w3id.org/class/hochschulfaechersystematik/scheme': 'DFÄ',
 'http://digicult.vocnet.org/sachgruppe': 'hessischesystematik',
 'https://www.ixtheo.de/classification/': 'IxTheo',
 'http://bartoc.org/en/node/730': 'BOS',
 'http://uri.gbv.de/terminology/thema': 'thema',
 'http://uri.gbv.de/terminology/dfg/': 'DFG',
 'http://msc2010.org/resources/MSC/2010/msc2010/': 'MSC',
 'http://uri.gbv.de/terminology/prizepapers_actor_actor_relation/': 'prizepapers_actor_actor_relation',
 'http://uri.gbv.de/terminology/person_relation/': 'person_relation',
 'http://bartoc.org/en/node/18928': 'SSG',
 'http://uri.gbv.de/terminology/prizepapers_place/': 'prizepapers_place',
 'http://id.loc.gov/vocabulary/iso639-1': 'language_iso639_1',
 'http://bartoc.org/en/node/313': 'STW',
 'http://iconclass.org/rdf/2011/09/': 'iconclass',
 'http://uri.gbv.de/terminology/part_of_speech/': 'part_of_speech',
 'http://uri.gbv.de/terminology/museenstade_ortsstadtteile/': 'museenstade_ortsstadtteile',
 'http://uri.gbv.de/terminology/museenstade_strassennamen/': 'museenstade_strassennamen',
 'http://w3id.org/nkos/nkostype': 'nkostype',
 'http://bartoc.org/en/node/454': 'LCSH',
 'http://bartoc.org/en/node/294': 'TheSoz',
 'http://bartoc.org/en/node/18915': 'ZDB-FGS'}


for mapping in count_mappings:
    mapping['from'] = uri_to_not.get(mapping['from'], mapping['from'])
    mapping['to'] = uri_to_not.get(mapping['to'], mapping['to'])

merged_mappings = {}
for mapping in count_mappings:
    key = (mapping['from'], mapping['to'])
    weight = mapping['weight']
    if key in merged_mappings:
        merged_mappings[key] += weight
    else:
        merged_mappings[key] = weight

count_mappings = [{'from': key[0], 'to': key[1], 'weight': value} for key, value in merged_mappings.items()]



source_nodes = list(set([link['from'] for link in count_mappings]))
target_nodes = list(set([link['to'] for link in count_mappings]))

source_node_ids = {node: i for i, node in enumerate(source_nodes)}
target_node_ids = {node: i + len(source_nodes) for i, node in enumerate(target_nodes)}

link_sources = []
link_targets = []

weights = [link['weight'] for link in count_mappings]

node_labels = source_nodes + target_nodes

log_weights = np.log(weights)
max_log_weight = max(log_weights)
min_log_weight = min(log_weights)
scaled_log_weights = [(w - min_log_weight) / (max_log_weight - min_log_weight) for w in log_weights]

for link in count_mappings:
    if link['from'] in source_nodes and link['to'] in target_nodes:
        link_sources.append(source_node_ids[link['from']])
        link_targets.append(target_node_ids[link['to']])

hover_text = [f"Anzahl: {w}" 
              for w in weights]
color_mapping = {}
for label in node_labels:
    if label not in color_mapping:
        color_mapping[label] = np.random.choice(range(256), size=3)  # Random color for each unique label

# Assign colors to nodes based on the mapping
node_colors = [f'rgb({",".join(map(str, color_mapping[label]))})' for label in node_labels]

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=node_labels,
        color=node_colors  # Assign colors to nodes
    ),
    link=dict(
        source=link_sources,
        target=link_targets,
        value=[w * 10 for w in scaled_log_weights],
        customdata=hover_text,
        hovertemplate='%{customdata}<extra></extra>'
    ))])

fig.update_layout(title_text="Cocoda Mappings", font_size=10)

fig.write_html("sankey_graph.html")

