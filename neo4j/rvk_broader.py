import csv

file1_path = 'rvk_bk_mappings.tsv'

broader = {}
with open(file1_path, 'r', newline='') as file1:
    reader = csv.reader(file1, delimiter='\t')
    header = next(reader)
    for row in reader:
        if row:
            notation = row[1]
            broader[notation] = row[7]

done = []
for narrower, broader in broader.items():
    if narrower not in done:
        if broader:
            print(f"\"{narrower}\" -> \"{broader}\" :broader")
        print(f"\"{narrower}\" :rvk notation:\"{narrower}\"")
        done.append(narrower)