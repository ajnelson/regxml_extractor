#!/usr/bin/python3

__version__ = "0.0.1"

import hivex

def main():
    pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug")
    parser.add_argument("hive")
    parser.parse_args()

    main()
