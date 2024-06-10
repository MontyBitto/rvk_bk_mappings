import sys
from lxml import etree

def extract_notations(node, parent=""):
    notations = []
    if 'notation' in node.attrib:
        notation = node.attrib['notation']
        notations.append([notation, parent])
    else:
        notation = parent
    for child in node:
        notations.extend(extract_notations(child, notation))
    return notations

xml_data = sys.stdin.buffer.read()

xml_str = xml_data.decode('utf-8')
if xml_str.startswith('<?xml'):
    xml_str = xml_str.split('?>', 1)[1]

tree = etree.fromstring(xml_str)
root = tree
notations = extract_notations(root)

for narrower, broader in notations:
    if broader:
        print(f"\"{narrower}\" -> \"{broader}\" :broader")
    print(f"\"{narrower}\" :rvk notation:\"{narrower}\"")
