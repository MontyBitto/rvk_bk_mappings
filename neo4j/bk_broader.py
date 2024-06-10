import json
import sys

input_file = sys.argv[1]
data = {}

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        entry = json.loads(line.strip())
        
        notation = entry.get('notation', [None])[0]
        
        broader_notations = entry.get('broader', [])
        for broader in broader_notations:
            broader_notation = broader.get('notation', [None])[0]
            data[notation] = broader_notation

done = []
for narrower, broader in data.items():
        
    print(f"\"{narrower}\" -> \"{broader}\" :broader")
    if narrower not in done: 
        print(f"\"{narrower}\" :bk notation:\"{narrower}\"")   
        done.append(narrower)
    if broader not in done:
        print(f"\"{broader}\" :bk notation:\"{broader}\"")   
        done.append(broader)