from lxml import etree
import sys

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

xml_content_bytes = sys.stdin.buffer.read()
root = etree.XML(xml_content_bytes)
notations = extract_notations(root)

for narrower, broader in notations:
    if broader != "": 
        print(f"\"http://rvk.uni-regensburg.de/nt/{narrower}\" -> \"http://rvk.uni-regensburg.de/nt/{broader}\" :broader")
    print(f"\"http://rvk.uni-regensburg.de/nt/{narrower}\" :rvk :concept notation:\"{narrower}\"")   