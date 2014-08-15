#!/usr/bin/python3

__version__ = "0.0.4"

import functools
import base64
import logging
import sys
import time
import xml.etree.ElementTree as ET
import os

_logger = logging.getLogger(os.path.basename(__file__))

import hivex
import dfxml
import Objects

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
    #_logger.debug("_hivex_walk (%r, %r, %r)" % (h, node, pathstack))
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
    regxml_object_from_hive(args.hive).print_regxml(output_fh=sys.stdout)

def regxml_object_from_hive(hive, fileobject=None):
    h = hivex.Hivex (args.hive)
    _logger.debug(dir(h))
    r = h.root()
    _logger.debug("root = %r" % r)

    rxdoc = Objects.RegXMLObject()
    rxdoc.version = "0.2.0"
    rxdoc.interpreter = "Python %s.%s.%s" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    rxdoc.program = sys.argv[0]
    rxdoc.program_version = __version__
    rxdoc.command_line = " ".join(sys.argv)
    

    #NOTE: This is remaining metadata not yet integrated into RegXML Objects.
    meta = dict()
    meta["hivex_version"] = "TODO" #TODO
    meta["start_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    hive_object = Objects.HiveObject()

    #Record timestamp of hive
    ts = h.last_modified()
    dft = dftime_from_windows_filetime(ts)
    if not dft is None:
        hive_object.mtime = dft

    if not fileobject is None:
        hive_object.original_fileobject = fileobject

    #Walk hive structure
    for (nodepath, nodes, values) in hivex_walk(h, r):
        #_logger.debug("(n, ns, vs) = %r" % ((n, ns, vs),))
        for node in nodes:
            obj = hivex_node_to_Object(h, node, nodepath)
            hive_object.append(obj)
        for value in values:
            obj = hivex_value_to_Object(h, value, nodepath)
            hive_object.append(obj)

def hivex_node_to_Object(h, node, nodepath):
    return _hivex_cell_to_Object(h, node, nodepath, "k")

def hivex_value_to_Object(h, node, nodepath):
    return _hivex_cell_to_Object(h, node, nodepath, "v")

def _hivex_cell_to_Object(h, cell, nodepath, celltype):
    _logger.debug("_hivex_cell_to_Element(h, %r, %r, %r)" % (cell, nodepath, celltype))

    assert celltype in ["k","v"]

    co = Objects.CellObject()

    #Add parent object reference
    #Because hive nodes record parent references, use Hivex's API in addition to tracking the node path when possible.
    #Note that hive values don't record parent references.
    if h.root() == cell:
        #The root element does not have a usable parent reference (#TODO Check this - is it null, or garbage values?)
        co.root = True
    else:
        parent_node_from_walk = nodepath[-1]

        parent = Objects.CellObject()
        parent.id = parent_node_from_walk 

        if celltype == "k":
            parent_node_from_node = h.node_parent(cell)
            #Check for a discrepancy, between parent recorded in the key, and the walk.
            if parent_node_from_node != parent_node_from_walk:
                parent.error = "Parent reference discrepancy.  Parent ID from walk: %r.  Parent ID from node: %r." % (parent_node_from_walk, parent_node_from_node)

        co.parent_object = parent

    #Fetch current cell's name
    #TODO Handle all encoding with base64 care
    cellname = get_cell_name(h, cell, celltype)
    cellname_length = None
    if celltype == "v":
        cellname_length = h.value_key_len(cell)

    #Add encoded cellpath
    namestack = []
    #If the nodepath is provided, prepend the empty string to the path so it is absolute
    if isinstance(nodepath,list):
        namestack.append("")
        for pathcell in nodepath:
            namestack.append(get_cell_name(h, pathcell, "k"))
    namestack.append(cellname)
    #TODO Handle encoding
    cell_full_path = "\\".join(namestack)
    co.cellpath = cell_full_path

    #Add encoded cell name
    if not cellname is None:
        co.basename = cellname
        co.basename_length = cellname_length #Not specified yet whether this will be character length or byte length.

    #Add id
    co.id = cell

    #Add the cell's structural type
    co.name_type = celltype

    #Add value size, if a value
    if celltype == "v":
        type_and_len = h.value_type(cell)
        valuesize = str(type_and_len[1])
        if type_and_len is None:
            _logger.error("Error retrieving type and length of value cell %r." % cell)
            co.error("Error retrieving type and length of value cell %r." % cell)
        else:
            co.valuesize = valuesize

    #Add the cell's allocation status
    #(Everything found with Hivex at the moment is allocated)
    co.alloc = True

    #Add the key's mtime
    if celltype == "k":
        timestamp_numeric = h.node_timestamp(cell)
        co.mtime = dftime_from_windows_filetime(timestamp_numeric)
        co.mtime.prec = "100ns"

    #Add the value's data
    #There is a bias to blindly base64 encoding everything, due to data types not being trustworthy
    if celltype == "v":
        type_and_data = h.value_value(cell)
        _logger.debug("type_and_data = %r" % (type_and_data,))

        value_type = HIVE_VALUE_TYPES[type_and_data[0]]

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
            _logger.error("Exception: " + sys.exc_info()[0])
            pass
        conversions = dict()
        if not as_int is None:
            conversions["integer"] = as_int
        if not as_string is None:
            conversions["string"] = as_string
        if not as_string_list is None:
            conversions["string_list"] = as_string_list

        co.data = b64chars
        co.data_encoding = "base64"
        co.data_type = value_type
        if len(conversions) > 0:
            co.data_conversions = conversions

    #Add all byte_runs
    if celltype == "k":
        dslength = h.node_struct_length(cell)

        co.name_brs = Objects.ByteRuns()
        co.name_brs.facet = "name"

        tmpo = Objects.ByteRun()
        tmpo.file_offset = cell
        tmpo.len = dslength
        co.name_brs.append(tmpo)

        #TODO Hivex will need extending to report the location of child reference lists.

    elif celltype == "v":
        dslength = h.value_struct_length(cell)
        length_and_offset = h.value_data_cell_offset(cell) #TODO The documentation on this is wrong - what's returned is length, offset.

        co.name_brs = Objects.ByteRuns()
        co.name_brs.facet = "name"
        tmpo = Objects.ByteRun()
        tmpo.file_offset = cell
        tmpo.len = dslength
        co.name_brs.append(tmpo)

        co.data_brs = Objects.ByteRuns()
        co.data_brs.facet = "data"
        tmpo = Objects.ByteRun()
        if length_and_offset == (0,0):
            #The (0,0) pair is the sentinel value returned for inlined data. Calculate data offset based on value struct knowledge.
            br_offset = cell + 0xc
            br_len = valuesize
        else:
            br_offset = length_and_offset[1]
            br_len = length_and_offset[0]
        tmpo.file_offset = br_offset
        tmpo.len = br_len
        co.data_brs.append(tmpo)

    return co

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
