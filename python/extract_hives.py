#!/usr/bin/env python
"""
For usage instructions, see the argument parser description below, or run this script without arguments.
"""

__version__ = "0.1.0"

import dfxml,fiwalk
import sys,os,datetime
import argparse

tally = 0

def proc_dfxml(fi):
    global tally
    global hivexml_command
    basename = os.path.basename(fi.filename()).lower()
    #Names noted in Carvey, 2011 (_Windows Registry Forensics_), page 18
    if fi.filename().lower().endswith(("ntuser.dat", "system32/config/sam", "system32/config/security", "system32/config/software", "system32/config/system", "system32/config/components", "local settings/application data/microsoft/windows/usrclass.dat")):
        outfilename = os.path.abspath(str(tally) + ".hive")
        print("\t".join(map(str, [outfilename, fi.filename(), fi.mtime(), fi.atime(), fi.ctime(), fi.crtime()])))
        outfile = open(outfilename, "wb")
        outfile.write(fi.contents())
        outfile.close()
        if hivexml_command:
            command_string = hivexml_command + " " + outfilename + ">" + outfilename+".regxml" + " 2>" + outfilename + ".err.log"
            sysrc = os.system(command_string)
            if sysrc:
                sys.stderr.write("Error, see err.log: " + command_string + "\n")
        tally += 1

if __name__=="__main__":
    global hivexml_command

    parser = argparse.ArgumentParser(description="Find registry files in imagefile and dump hives to files in pwd in the order they're encountered, with a manifest printed to stdout.")
    parser.add_argument("-x", "--xml", dest="dfxml_file_name", help="Already-created DFXML file for imagefile")
    parser.add_argument("--hivexml", dest="hivexml_command", action="store_const", const="hivexml", default="",  help="Run hivexml command on each hive, producing output at <hive>.regxml, stderr at <hive>.err.log")
    parser.add_argument("imagefilename", help="Image file")
    args = parser.parse_args()
    
    hivexml_command = args.hivexml_command

    xmlfh = None
    if args.dfxml_file_name != None:
        xmlfh = open(args.dfxml_file_name, "r")

    fiwalk.fiwalk_using_sax(imagefile=open(args.imagefilename, "r"), xmlfile=xmlfh, callback=proc_dfxml)
