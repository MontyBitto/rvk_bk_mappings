from lxml import etree

def extract_notations(node, parent=""):
    notations = []
    if 'notation' in node.attrib:
        notation = node.attrib['notation']
        notations.append([notation, parent])
    else:
        notation = parent  # Pass down the parent notation if current node has none
    for child in node:
        notations.extend(extract_notations(child, notation))
    return notations

# Parse the XML file
tree = etree.parse("rvko_2024_1.xml")
root = tree.getroot()

# Extract notations
notations = extract_notations(root)

for narrower, broader in notations:
    if broader:
        print(f"\"{narrower}\" -> \"{broader}\" :broader")
    print(f"\"{narrower}\" :rvk notation:\"{narrower}\"")
