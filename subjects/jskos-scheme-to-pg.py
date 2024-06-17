import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('voc', type=str)
parser.add_argument('input', type=argparse.FileType('r'))
args = parser.parse_args()

input_file = args.input
voc = args.voc

data = {}

for line in input_file:
    entry = json.loads(line.strip())

    notation = entry.get('notation', [None])[0]
    uri = entry.get('uri', [None])
    data[notation] = [uri]
    broader = entry.get('broader', [])
    if broader != []:
        broader_uri = broader[0].get('uri', [None])
        data[notation].append(broader_uri)

for narrower, uris in data.items():
    if len(uris)>1:
        print(f"\"{uris[0]}\" -> \"{uris[1]}\" :broader")
    print(f"\"{uris[0]}\" :{voc} :concept notation:\"{narrower}\"")