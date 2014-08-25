#!/opt/local/bin/python3.3

#sudo port install py33-enum34

__version__ = "0.0.3"

import sys
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

from Registry import Registry

import Objects

_paths = set()

def cell_walk(cell_path):
    """Like os.walk().  However, all lists are not paths, but RegistryKey or RegistryValue objects."""
    #_logger.debug("cell_walk(%r)" % cell_path)
    yield (cell_path, cell_path[-1].subkeys(), cell_path[-1].values())

    for key in cell_path[-1].subkeys():
        yield from cell_walk(cell_path + [key])

def CellObject_from_RegistryKey(rk, parent=None):
    if rk is None:
        return None

    c = Objects.CellObject()

    c.alloc = True
    c.basename = rk.name()
    c.cellpath = rk.path()
    c.mtime = rk.timestamp()
    c.name_type = "k"
    c.parent_object = CellObject_from_RegistryKey(parent)

    return c

def main():
    global _paths
    global args

    reg = Registry.Registry(args.hive_file)

    r = Objects.RegXMLObject()
    h = Objects.HiveObject()

    for (iter_no, (cell_path, subkeys, values)) in enumerate(cell_walk([reg.root()])):
        #_logger.debug(cell_path[-1].path())

        #if tally == 1:
        #    _logger.debug("subkeys = %r." % subkeys)
        #if tally > 10:
        #    break

        c = CellObject_from_RegistryKey(cell_path[-1])
        c.id = iter_no
        if iter_no == 0:
            c.root = True

        if c.cellpath in _paths:
            _logger.warning("Encountered a path multiple times: %r." % c.cellpath)
        else:
            _paths.add(c.cellpath)

        h.append(c)
    r.append(h)
    r.print_regxml(sys.stdout)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("hive_file")
    args  = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
