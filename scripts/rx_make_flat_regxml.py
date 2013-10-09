#!/usr/bin/python3

__version__ = "0.0.1"

import hivex
import flatten_regxml
import functools
import base64
import logging
import sys
import time
import xml.etree.ElementTree as ET
import dfxml

XMLNS_REGXML = "http://www.forensicswiki.org/wiki/RegXML"
ET.register_namespace("", XMLNS_REGXML)

HIVE_VALUE_TYPES = {
  0: "REG_NONE",
  1: "REG_SZ",
  2: "REG_EXPAND_SZ",
  3: "REG_BINARY",
  4: "REG_DWORD",
  5: "REG_DWORD_BIG_ENDIAN",
  6: "REG_LINK",
  7: "REG_MULTI_SZ",
  8: "REG_RESOURCE_LIST",
  9: "REG_FULL_RESOURCE_DESCRIPTOR",
  10: "REG_RESOURCE_REQUIREMENTS_LIST",
  11: "REG_QWORD"
}

def _hivex_walk (h, node, pathstack):
    """
    Generator.  Yields triplet:
    * nodepath: descent list of nodes from the walk root, ending in the current internal node.
    * nodes: List 
    * values: List
    """
    logging.debug("_hivex_walk (%r, %r, %r)" % (h, node, pathstack))
    pathstack.append(node)
    nodes = h.node_children(node)
    values = h.node_values(node)
    yield (pathstack, nodes, values)
    for n in nodes:
        for result in _hivex_walk (h, n, pathstack):
            yield result
    pathstack.pop()

def hivex_walk (h, node):
    #TODO assert 'node' is a node
    for result in _hivex_walk (h, node, []):
        yield result

@functools.lru_cache(maxsize=None)
def get_cell_name(h, cell, celltype):
    assert celltype in ["k","v"]
    if celltype == "k":
        return h.node_name(cell)
    elif celltype == "v":
        return h.value_key(cell)

def main ():
    h = hivex.Hivex (args.hive)
    logging.debug(dir(h))
    r = h.root()
    logging.debug("root = %r" % r)
    
    meta = dict()
    meta["XMLNS_REGXML"] = XMLNS_REGXML
    meta["program"] = sys.argv[0]
    meta["version"] = __version__
    meta["interpreter"] = "Python %s.%s.%s" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    meta["hivex_version"] = "TODO" #TODO
    meta["command_line"] = " ".join(sys.argv)
    meta["start_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print("""\
<?xml version="1.0"?>
<regxml
  xmlns="%(XMLNS_REGXML)s"
  version="2.0">
  <creator>
    <program>%(program)s</program>
    <version>%(version)s</version>
  </creator>
  <build_environment>
    <interpreter>%(interpreter)s</interpreter>
    <library name="Hivex" version="%(hivex_version)s"/>
  </build_environment>
  <execution_environment>
    <command_line>%(command_line)s</command_line>
    <start_time>%(start_time)s</start_time>
  </execution_environment>
  <hive>""" % meta)

    #Record timestamp of hive
    ts = h.last_modified()
    dft = dftime_from_windows_filetime(ts)
    if not dft is None:
        print("""\
    <mtime prec="100ns">%s</mtime>""" % str(dft))

    #Walk hive structure
    for (nodepath, nodes, values) in hivex_walk(h, r):
        #logging.debug("(n, ns, vs) = %r" % ((n, ns, vs),))
        for value in values:
            elem = hivex_value_to_Element(h, value, nodepath)
            print(dfxml.ET_tostring(elem, encoding="unicode"))
            del elem
        for node in nodes:
            elem = hivex_node_to_Element(h, node, nodepath)
            print(dfxml.ET_tostring(elem, encoding="unicode"))
            del elem
    print("""\
  </hive>
</regxml>""")

def hivex_node_to_Element(h, node, nodepath):
    return _hivex_cell_to_Element(h, node, nodepath, "k")

def hivex_value_to_Element(h, node, nodepath):
    return _hivex_cell_to_Element(h, node, nodepath, "v")

def _hivex_cell_to_Element(h, cell, nodepath, celltype):
    logging.debug("_hivex_cell_to_Element(h, %r, %r, %r)" % (cell, nodepath, celltype))

    assert celltype in ["k","v"]

    e = ET.Element("cellobject")

    #Add parent object reference
    #Because hive nodes record parent references, use Hivex's API in addition to tracking the node path when possible.
    #Note that hive values don't record parent references.
    if h.root() == cell:
        #The root element does not have a usable parent reference (#TODO Check this - is it null, or garbage values?)
        e.attrib["root"] = "1"
    else:
        tmp = ET.Element("parent_object")
        tmp2 = ET.Element("id")
        parent_node_from_walk = nodepath[-1]
        tmp2.text = str(parent_node_from_walk)
        tmp2.attrib["from_walk"] = "1"
        tmp.append(tmp2)
        if celltype == "k":
            parent_node_from_node = h.node_parent(cell)
            #If there is a discrepancy, add another id; if there's no discrepancy, the first parent id reference gets the from_key tag.
            if parent_node_from_node != parent_node_from_walk:
                del tmp2
                tmp2 = ET.Element("id")
                tmp2.text = str(parent_node_from_node)
            tmp2.attrib["from_key"] = "1"
        del tmp2
        e.append(tmp)

    #Fetch current cell's name
    #TODO Handle all encoding with base64 care
    cellname = get_cell_name(h, cell, celltype)
    cellname_length = None
    if celltype == "v":
        cellname_length = h.value_key_len(cell)

    #Add encoded cellpath
    tmp = ET.Element("cellpath")
    namestack = []
    #If the nodepath is provided, prepend the empty string to the path so it is absolute
    if isinstance(nodepath,list):
        namestack.append("")
        for pathcell in nodepath:
            namestack.append(get_cell_name(h, pathcell, "k"))
    namestack.append(cellname)
    #TODO Handle encoding
    cell_full_path = "\\".join(namestack)
    tmp.text = cell_full_path
    e.append(tmp)

    #Add encoded cell name
    tmp = ET.Element("name")
    if not cellname is None:
        if not cellname_length is None:
            tmp.attrib["recorded_length"] = str(cellname_length)
        tmp.text = cellname
        e.append(tmp)

    #Add id
    tmp = ET.Element("id")
    tmp.text = str(cell)
    e.append(tmp)

    #Add the cell's structural type
    tmp = ET.Element("name_type")
    tmp.text = celltype
    e.append(tmp)

    #Add value size, if a value
    if celltype == "v":
        type_and_len = h.value_type(cell)
        valuesize = str(type_and_len[1])
        if type_and_len is None:
            logging.error("Error retrieving type and length of value cell %r." % cell)
        else:
            tmp = ET.Element("valuesize")
            tmp.text = valuesize
            e.append(tmp)

    #Add the cell's allocation status
    tmp = ET.Element("alloc")
    #(Everything found at the moment is allocated)
    tmp.text = "1"
    e.append(tmp)

    #Add the key's mtime
    if celltype == "k":
        tmp = ET.Element("mtime")
        timestamp_numeric = h.node_timestamp(cell)
        timestamp_dftime = dftime_from_windows_filetime(timestamp_numeric)
        tmp.text = str(timestamp_dftime)
        tmp.attrib["prec"] = "100ns"
        e.append(tmp)

    #Add the value's data
    #There is a bias to blindly base64 encoding everything, due to data types not being trustworthy
    if celltype == "v":
        type_and_data = h.value_value(cell)
        value_type = HIVE_VALUE_TYPES[type_and_data[0]]
        logging.debug("type_and_data = %r" % (type_and_data,))

        b64bytes = base64.b64encode(type_and_data[1])
        b64chars = b64bytes.decode()

        tmp = ET.Element("data")
        tmp.attrib["type"] = value_type

        as_int = None
        as_string = None
        as_string_list = None
        try:
            if value_type in ["REG_NONE"]:
                pass

            #Since binary blobs are so frequently overloaded, blindly try interpreting them.  Python3 semantics in a try block are: Last successful assignment wins.
            #TODO Check to see if the Hivex library jumps ship early on a type check
            elif value_type in ["REG_BINARY"]:
                try:
                    as_string = h.value_string(cell)
                    as_int = h.value_dword(cell)
                    as_int = h.value_qword(cell)
                except:
                    pass

            #TODO REG_LINK might be wrong to use here; I forget what's stashed in this cell type.
            elif value_type in ["REG_SZ", "REG_EXPAND_SZ", "REG_LINK"]:
                as_string = h.value_string(cell)

            elif value_type in ["REG_MULTI_SZ"]:
                as_string_list = h.value_multiple_strings(cell)

            elif value_type in ["REG_DWORD", "REG_DWORD_BIG_ENDIAN"]:
                as_int = h.value_dword(cell)

            elif value_type in ["REG_QWORD"]:
                as_int = h.value_qword(cell)

            #This last block simply notes the types not investigated
            elif value_type in ["REG_RESOURCE_LIST", "REG_FULL_RESOURCE_DESCRIPTOR", "REG_RESOURCE_REQUIREMENTS_LIST"]:
                pass

        except e:
            logging.error("Exception: " + sys.exc_info()[0])
            pass
        if not as_int is None:
            e.append(ET.Comment("As a number: %r" % as_int))
        if not as_string is None:
            e.append(ET.Comment("As a string: %r" % as_string))
        if not as_string_list is None:
            e.append(ET.Comment("As a string list: %r" % as_string_list))

        tmp.attrib["encoding"] = "base64"
        tmp.text = b64chars
        e.append(tmp)

    #Add all byte_runs
    #TODO
    #tmp = ET.Element("byte_runs")
    #e.append(tmp)

    return e

def dftime_from_windows_filetime(wft):
    """
    Note that a filetime of 0 is interpreted as a null timestamp.  No Windows system truly cares about the year 1600.
    """
    #TODO Add fractional seconds to timestamps in the DFXML library.
    if wft == 0:
        return None

    WINDOWS_TICK = 10000000
    SEC_TO_UNIX_EPOCH = 11644473600

    timestamp = wft / 10000000.0 - 11644473600
    return dfxml.dftime(timestamp)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser ()
    parser.add_argument ("-d", "--debug", action="store_true")
    parser.add_argument ("hive")
    args = parser.parse_args ()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main ()
