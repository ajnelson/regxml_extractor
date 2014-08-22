#!/opt/local/bin/python3.3

#sudo port install py33-enum34

import sys
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

from Registry import Registry

def cell_walk(cell_path):
    """Like os.walk().  However, all lists are not paths, but RegistryKey or RegistryValue objects."""
    #_logger.debug("cell_walk(%r)" % cell_path)
    yield (cell_path, cell_path[-1].subkeys(), cell_path[-1].values())

    for key in cell_path[-1].subkeys():
        yield from cell_walk(cell_path + [key])

def main():
    global args
    reg = Registry.Registry(args.hive_file)

    for (iter_no, (cell_path, subkeys, values)) in enumerate(cell_walk([reg.root()])):
        #_logger.debug(cell_path[-1].path())

        #if tally == 1:
        #    _logger.debug("subkeys = %r." % subkeys)
        #if tally > 10:
        #    break

        print(str(cell_path[-1].timestamp()) + "\t" + cell_path[-1].path())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("hive_file")
    args  = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
