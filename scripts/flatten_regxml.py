#!/usr/bin/env python3

"""
Converts hivexml output to flat-hierarchy RegXML.
"""

__version__ = "0.0.2"

import sys
import os
import logging

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import datetime
import dfxml

def main():
    xmlout = sys.stdout

    meta = dict()
    meta["creator_program"] = os.path.basename(sys.argv[0])
    meta["creator_version"] = __version__
    meta["command_line"] = " ".join(sys.argv)
    meta["hivex_version"] = "TODO"
    meta["image_filename"] = args.regxml_file
    meta["interpreter"] = "Python %d.%d.%d" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    meta["start_time"] = dfxml.dftime(datetime.datetime.now())

    xmlout.write("""\
<?xml version='1.0' encoding='UTF-8'?>
<regxml version='2.0'>
  <metadata 
  xmlns='https://github.com/ajnelson/regxml_extractor'
  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' 
  xmlns:dc='http://purl.org/dc/elements/1.1/'>
    <dc:type>Windows Registry Hive</dc:type>
  </metadata>
  <creator version='1.0'>
    <program>%(creator_program)s</program>
    <version>%(creator_version)s</version>
    <build_environment>
      <interpreter>%(interpreter)s</interpreter>
      <library name="hivex" version="%(hivex_version)s"/>
    </build_environment>
    <execution_environment>
      <command_line>%(command_line)s</command_line>
      <start_time>%(start_time)s</start_time>
    </execution_environment>
  </creator>
  <source>
    <image_filename>%(image_filename)s</image_filename>
  </source>
  <hive>
""" % meta)

    indent = 4

    cell_dict = dict()
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

                #Handling null names: None -> ""
                if name_stack[-1] is None:
                    name_stack[-1] = ""

            elif event == "end":
                cell_path = "\\".join(name_stack)
                name_stack.pop()

                x = ET.Element("cellpath")
                x.text = cell_path
                elem.insert(0, x)

                #Convert tag
                #value -> valueobject, {node,key} -> keyobject
                if elem.tag == "value":
                    elem.tag += "object"
                else:
                    elem.tag = "keyobject"

                #At this point, all of the child nodes and values have been parsed.  So, throw them away.
                for tagname in ["key", "value"]:
                    for parsed_cell in elem.findall(".//" + tagname + "object"):
                        elem.remove(parsed_cell)

                cell_dict[cell_path] = ET.tostring(elem, encoding="unicode")

    for cell_path in sorted(cell_dict.keys()):
        xmlout.write(" " * indent)
        xmlout.write(cell_dict[cell_path])
        xmlout.write("\n")
    xmlout.write("  </hive>\n")
    xmlout.write("</regxml>\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("regxml_file")
    args = parser.parse_args()

    main()
