from xml.etree import ElementTree
def strip_tag_name(t):
    idx = k = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t
tree = ElementTree.parse('namespace_test.xml')
print(tree.getroot())
print(tree.getroot().tag)
for child in tree.getroot():
    print(strip_tag_name(child.tag))

