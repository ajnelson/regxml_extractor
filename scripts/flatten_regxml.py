#!/usr/bin/env python3

import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def main():
    name_stack = []
    for event, elem in ET.iterparse(args.regxml_file, ("start","end")):
        #Debug
#        sys.stderr.write(event)
#        sys.stderr.write('\t')
#        sys.stderr.write(elem.tag)
#        sys.stderr.write('\t')
#        sys.stderr.write(repr(elem.attrib))
#        sys.stderr.write('\n')

        if elem.tag in ["node", "key", "value"]:
            if event == "start":
                if elem.tag in ["node", "key"]:
                    name_stack.append(elem.attrib.get("name"))
                elif elem.tag == "value":
                    name_stack.append(elem.attrib.get("key"))
#                sys.stderr.write("+\t%r\n" % (name_stack,))
            elif event == "end":
                x = ET.SubElement(elem,"cellpath") #TODO Use ET.Element.insert instead to get cellpath as first child
                x.text = "\\".join(name_stack)
                name_stack.pop()
                #value -> valueobject, {node,key} -> keyobject
                if elem.tag == "value":
                    elem.tag += "object"
                else:
                    elem.tag = "keyobject"

                #At this point, all of the child nodes and values have been parsed.  So, throw them away.
                for tagname in ["key", "value"]:
                    for parsed_cell in elem.findall(".//" + tagname + "object"):
                        elem.remove(parsed_cell)

                print(ET.tostring(elem, encoding="unicode"))
                print()
                print()
                print()
#                sys.stderr.write("-\t%r\n" % (name_stack,))
#        elem.clear()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("regxml_file")
    args = parser.parse_args()

    main()
