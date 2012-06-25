#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $(basename $0) <re output sequence>" >&2
  echo "The output sequence file should list the absolute paths to RegXML Extractor output directories, one per line, recorded in ascending sequence order.  For example, if case Foo had images 'baseline',  'installed', and 'cleaned', their sequence file may be:" >&2
  echo "" >&2
  echo "/data/regxml_extractor/Foo/baseline" >&2
  echo "/data/regxml_extractor/Foo/installed" >&2
  echo "/data/regxml_extractor/Foo/cleaned" >&2
  exit 1
fi

#(This should probably entirely be a Python script)

#Determine _hive_ sequences from disk image sequences
#  (This logic is already done in rx_make_database.py)

#Run rdifference.py on each hive sequence
#  (rdifference should ultimately output to a database)

