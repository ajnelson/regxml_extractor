#!/usr/bin/env python3

"""
Converts hivexml output to flat-hierarchy RegXML.
"""

__version__ = "0.1.0"

import sys
import os
import logging

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import datetime
import dfxml

class Encodeable():
    """
    Note that null cell names are simply converted to "".
    """
    def __init__(self, element_name, data=None, encoding=None):
        if not isinstance(element_name, str):
            raise Exception("Element name must be a string.")
        self._element_name = element_name
        self._data = data
        self._encoding = encoding

    def __str__(self):
        if self._encoding is None:
            return self._data or ""
        elif self._encoding == "base64":
            return dfxml.safe_b64decode(self._data) or ""
        else:
            raise Exception("Decodings other than base64 not yet implemented.")

    def to_Element(self):
        retval = ET.Element(self._element_name)
        if self._encoding:
            retval.attrib["encoding"] = self._encoding
        retval.text = self._data or ""
        return retval

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
<regxml 
  xmlns='http://www.forensicswiki.org/wiki/RegXML'
  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' 
  xmlns:dc='http://purl.org/dc/elements/1.1/'
  version='2.0b'>
  <metadata>
    <dc:type>Windows Registry Hive</dc:type>
  </metadata>
  <creator>
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
                #Convert the cell's name attribute to an Element shim
                if elem.tag in ["node", "key"]:
                    cn = Encodeable("name", elem.attrib.get("name"), elem.attrib.get("name_encoding"))
                    elem.attrib.pop("name", None)
                    elem.attrib.pop("name_encoding", None)
                elif elem.tag == "value":
                    cn = Encodeable("name", elem.attrib.get("key"), elem.attrib.get("key_encoding"))
                    elem.attrib.pop("key", None)
                    elem.attrib.pop("key_encoding", None)
                name_stack.append(cn)

            elif event == "end":
                cell_path = "\\".join(map(str, name_stack))
                the_name = name_stack.pop()

                x = ET.Element("cellpath")
                x.text = cell_path
                elem.insert(0, x)

                elem.insert(1, the_name.to_Element())

                #Convert tag from key/value to cellobject with a name_type child
                #value -> valueobject, {node,key} -> keyobject
                name_type= "?"
                if elem.tag == "value":
                    name_type = "v"
                else:
                    name_type = "k"
                x = ET.Element("name_type")
                x.text = name_type
                elem.insert(2, x)
                elem.tag = "cellobject"

                #Note this alloc element is only true for Hivex on the modified 1.3.3 branch.
                x = ET.Element("alloc")
                x.text = "1"
                elem.insert(3, x)

                #Catch the 'default' attribute of value elements
                default_flag = elem.attrib.pop("default", None)
                if default_flag:
                    x = ET.Element("default")
                    elem.insert(4, x)

                #Convert value data to an element
                if name_type == "v":
                    value_elem = Encodeable("data", elem.attrib.get("value"), elem.attrib.get("value_encoding")).to_Element()
                    value_elem.attrib["type"] = elem.attrib["type"] #Values must have a type.  So if this fails, it's worth knowing.
                    elem.attrib.pop("value_encoding", None)
                    elem.attrib.pop("type", None)
                    elem.attrib.pop("value", None)
                    elem.insert(4, value_elem)

                #At this point, all of the child keys and values have been parsed.  So, throw them away.
                for parsed_cell in elem.findall(".//cellobject"):
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
