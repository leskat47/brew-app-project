import xml.etree.ElementTree as ET

tree = ET.parse("recipes.xml")
root = tree.getroot()

# for child in root:
#     for subchild in child:
#         print (subchild.tag).lower(), subchild.text
#     print "*" * 20

for child in root:
    for subchild in child:
        for hop in subchild:
            print hop.find('HOP').text


# for hop_name in root.iter('name'):
#     print hop.text