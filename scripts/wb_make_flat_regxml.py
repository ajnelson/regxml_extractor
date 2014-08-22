import sys
from Registry import Registry

reg = Registry.Registry(sys.argv[1])

#Print all keys in a Registry
def rec(key, depth=0):
    print "\t" * depth + key.path()

    for subkey in key.subkeys():
        rec(subkey, depth + 1)

rec(reg.root())
