#!/usr/bin/env python3

# Copyright (c) 2012, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University of California, Santa Cruz nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    

"""
For usage instructions, see the argument parser description below, or run this script without arguments.
"""

__version__ = "0.3.3"

import sys

import dfxml,fiwalk

import os,datetime
import argparse

import logging

def fileobject_is_hive(fi):
    """
    All matching happens on file name for now (we might want libmagic checks later).
    Names noted in Carvey, 2011 (_Windows Registry Forensics_), page 18.
    Some names found by pattern-matching in test data.
    """
    fn = fi.filename()

    if fn is None:
        return None

    if fn.lower().endswith((
      "ntuser.dat",
      "repair/sam",
      "repair/security",
      "repair/software",
      "repair/system",
      "system32/config/sam",
      "system32/config/security",
      "system32/config/software",
      "system32/config/system",
      "system32/config/components",
      "local settings/application data/microsoft/windows/usrclass.dat")):
        return True

    return False

def proc_dfxml(fi):
    global imageabspath
    if fileobject_is_hive(fi):
        outfile_basename = str(fi.tag("id")) + ".hive"
        outfile_abspath = os.path.abspath(outfile_basename)
        print("\t".join(map(str, [
          outfile_abspath,
          imageabspath,
          fi.filename(),
          fi.mtime(), fi.atime(), fi.ctime(), fi.crtime()
        ])))
        with open(outfile_abspath, "wb") as outfile:
            outfile.write(fi.contents())

if __name__=="__main__":
    global imageabspath

    parser = argparse.ArgumentParser(description="Find registry files in imagefile and dump hives to files in pwd in the order they're encountered, with a manifest printed to stdout.")
    parser.add_argument("-d", "--debug", help="Enable debug-level logging.", action="store_true")
    parser.add_argument("-x", "--xml", dest="dfxml_file_name", help="Already-created DFXML file for imagefile")
    parser.add_argument("imagefilename", help="Image file")
    args = parser.parse_args()

    xmlfh = None
    if args.dfxml_file_name != None:
        xmlfh = open(args.dfxml_file_name, "rb")
    imageabspath = os.path.abspath(args.imagefilename)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    fiwalk.fiwalk_using_sax(imagefile=open(imageabspath, "r"), xmlfile=xmlfh, callback=proc_dfxml)
