import xml.etree.ElementTree as ET

tree = ET.parse("hops.xml")
root = tree.getroot()

# for child in root:
#     for subchild in child:
#         print (subchild.tag).lower(), subchild.text
#     print "*" * 20

for child in root:
    name = child.find('NAME').text
    print name

# for hop_name in root.iter('name'):
#     print hop.text