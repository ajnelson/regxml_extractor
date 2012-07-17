#!/usr/bin/env python3

__version__ = "0.0.0"

import sys,fiwalk,dfxml,time
if sys.version_info < (3,1):
    raise RuntimeError("rdifference_db.py requires Python 3.1 or above")
import os
import argparse
#import rdifference

import collections

#TODO Convert this to provide content to Postgres
import sqlite3

def parse_sequence_map(map_file):
    """
    Expects tab-separated file with columns:
        * Sequence identifier string
        * Full path to RegXML Extractor output directory
        * Full path to Fiwalk (or similar) DFXML of disk image, if not in RE output directory
    Returns a mapping of file path sequence and DFXML.
    
    For example, this content:
        
        project0    /foo/project0_0.reout   /bar/project0_0.dfxml
        project1    /foo/project1_0.reout   /bar/project1_0.dfxml
        project0    /foo/project0_1.reout   /bar/project0_1.dfxml
    
    Would become:
        
        {
          "/foo/project0_0.reout":{
            "sequence":"project0",
            "dfxml":"/bar/project0_0.dfxml"
          },
          "/foo/project1_0.reout":{
            "sequence":"project1",
            "dfxml":"/bar/project1_0.dfxml"
          },
          "/foo/project0_1.reout":{
            "sequence":"project0",
            "dfxml":"/bar/project0_1.dfxml"
          }
        }
    
    Non-blank lines have a strict syntax enforcement check.
    
    Output directories must be unique.
    """
    retval = collections.OrderedDict()
    for (enumline, line) in enumerate(map_file):
        clean_line = line.strip()
        if clean_line != "":
            line_parts = clean_line.split("\t")
            assert len(line_parts) in [2,3]
            sequence_id = line_parts[0]
            re_out_dir = line_parts[1]
            #If no third entry, check reout directory for dfxml
            if len(line_parts) == 3:
                fiout = line_parts[2]
            else:
                fiout = os.path.join(re_out_dir, "fiout.dfxml")
            assert os.path.isdir(re_out_dir)
            assert os.path.isfile(fiout)
            assert re_out_dir not in retval
            retval[re_out_dir] = {
              "sequence": sequence_id,
              "dfxml": fiout
            }
    return retval

def sqlify_differences(state):
    assert isinstance(state, rdifference.HiveState)
    #TODO

def process_hive_sequence(hive_sequence):
    s = rdifference.HiveState(notimeline=True)
    for (enumreo, reo) in enumerate(sequence):
        s.process(reo)
        if enumreo > 0:
            sqlify_differences(s)
        s.next()

if __name__ == "__main__":
    global args
    parser = argparse.ArgumentParser(description="Format the Registry differences of a sequence of RegXML Extractor output directories.")
    parser.add_argument("sequence_map", type=argparse.FileType("r"), help="Tab-delimited file mapping sequence name to regxml_extractor.sh output directories; optional and _strongly encouraged_ third column specifies DFXML of disk image")
    parser.add_argument("re_out", nargs="+", help="regxml_extractor.sh output directories, in sequence order")
    parser.add_argument("--regress", action="store_true", help="Run unit tests and exit")
    parser.add_argument("-d", "--debug", help="Enable debug-level logging", action="store_true")
    args = parser.parse_args()
    
    if args.regress:
        from io import StringIO
        test_sequence_input = """project0\t/foo/project0_0.reout\t/bar/project0_0.dfxml
project1\t/foo/project1_0.reout\t/bar/project1_0.dfxml
project0\t/foo/project0_1.reout\t/bar/project0_1.dfxml"""
        test_sequence_dict = parse_sequence_map(test_sequence_input)
        assert test_sequence_dict == {
              "/foo/project0_0.reout":{
              "sequence":"project0",
              "dfxml":"/bar/project0_0.dfxml"
            },
              "/foo/project1_0.reout":{
              "sequence":"project1",
              "dfxml":"/bar/project1_0.dfxml"
            },
              "/foo/project0_1.reout":{
              "sequence":"project0",
              "dfxml":"/bar/project0_1.dfxml"
            }
        }

    
    if len(args.re_out) < 2:
        raise Exception("This script can only be invoked on more than one regxml_extractor.sh output directory.")

    #Begin processing directories -
    #but this is really, begin to process _hive_ sequences.
    #It is important to identify the sequences first.
    disk_image_sequence = parse_sequence_map(args.sequence_map)
    