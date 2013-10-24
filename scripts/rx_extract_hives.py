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

__version__ = "0.4.0"

import sys

import dfxml,fiwalk

import os,datetime
import argparse
import subprocess
import hashlib
import logging
import xml.etree.ElementTree as ET
import copy

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

def extract_byte_runs_to_file(fi, outfile, errlog=None, statlog=None):
        """
        (Unstable)
        (The DFXML library doesn't necessarily need a direct-to-file function.  The library could use a good iterator, though; maybe something like this function, that yields N bytes of stdout and the nullable exit status of tsk_img_cat, writing directly to the optional error log file.)

        Writes fileobject's contents to the file-like object stdout.  Uses TSK's img_cat.

        outfile, errlog, and statlog can all be either a string path or a file handle (has .fileno()).  The file number constraint is due to subprocess.Popen.

        @param outfile Copy-to location of the byte runs' contents.
        @param errlog Optional.  Logs stderr of img_cat up through the first call that exits non-0, if any.
        @param statlog Optional.  Logs '0' or the first non-zero exit status of img_cat.
        @return Returns the exit status of the last run img_cat process.
        """
        if fi.imagefile is None:
            raise ValueError("Imagefile is unknown.")

        if outfile is None:
            raise ValueError("Outfile cannot be null.")

        def _make_fh(maybef, binary=True):
            """
            Guarantee a file handle from a non-null String or File-like object.  Passing in None returns None; external logic should handle whether it's appropriate to call this function on None.
            """
            #logging.debug("maybef = %r", maybef)
            if maybef is None:
                return None
            retval = None
            if isinstance(maybef, str):
                mode = "w"
                if binary:
                    mode += "b"
                retval = open(maybef, mode)
            elif hasattr(maybedef, "fileno") and hasattr(maybedef, "write"):
                retval = maybef
            if retval is None:
                raise ValueError("Can't make a file handle out of (%r)." % maybef)
            return retval

        stdout_fh = _make_fh(outfile)
        stderr_fh = _make_fh(errlog)
        status_fh = _make_fh(statlog, False)

        #logging.debug("outfile = %r" % outfile)

        status_to_record = None
        try:
            br_counter = 0
            for run in fi.byte_runs():
                br_counter += 1
                #logging.debug("br_counter = %r" % br_counter)
                #logging.debug("stdout_fh = %r" % stdout_fh)
                if run.len == -1:
                    stdout_fh.write(b'\x00' * run.len)
                elif hasattr(run,'fill'):
                    #This assumes the encoding of the DFXML document was UTF-8.
                    #There is also an implicit assumption that the fill character is one byte long.
                    stdout_fh.write(bytes(run.fill, "utf-8") * run.len)
                else:
                    sector_size = 512
                    cmd = ["img_cat"]
                    cmd.append("-b")
                    cmd.append(str(sector_size))
                    cmd.append("-s")
                    cmd.append(str(run.img_offset//sector_size))
                    cmd.append("-e")
                    cmd.append(str((run.img_offset + run.len)//sector_size - 1))
                    cmd.append(fi.imagefile.name)
                    subprocess.check_call(cmd, stdout=stdout_fh, stderr=stderr_fh)
            if br_counter > 0:
                status_to_record = 0
        except subprocess.CalledProcessError as e:
            status_to_record = e.returncode

        if not status_fh is None:
            status_fh.write(str(status_to_record))
        return status_to_record

def proc_dfxml(fi):
    global xoutfh

    if not fileobject_is_hive(fi):
        return

    outfile_basename = str(fi.tag("id")) + ".hive"
    outfile_abspath = os.path.abspath(outfile_basename)
    imageabspath = os.path.abspath(fi.imagefile.name)

    #TODO Remove CSV results once other scripts don't depend on them.
    print("\t".join(map(str, [
      outfile_abspath,
      imageabspath,
      fi.filename(),
      fi.mtime(), fi.atime(), fi.ctime(), fi.crtime()
    ])))

    #Extract file
    rc = extract_byte_runs_to_file(
      fi,
      outfile = outfile_abspath,
      errlog  = outfile_abspath + ".err.log",
      statlog = outfile_abspath + ".status.log"
    )

    #Check extraction if possible
    checksum_match = None
    out_size = None
    out_sha1 = None
    if rc == 0:
        with open(outfile_abspath, "rb") as outfile_check_fh:
            data = outfile_check_fh.read()
            hasher = hashlib.new("sha1", data=data)
            out_sha1 = hasher.hexdigest()
        out_stat = os.stat(outfile_abspath)
        out_size = out_stat.st_size

    original_sha1 = fi.sha1()
    if not None in [original_sha1, out_sha1]:
        logging.debug("out_sha1 = %r" % out_sha1)
        logging.debug("original_sha1 = %r" % original_sha1)
        checksum_match = (out_sha1 == original_sha1)

    #Output DFXML manifest entry for this hive file
    if xoutfh:
        tmpel = ET.Element("fileobject")

        tmpname = ET.Element("filename")
        tmpname.text = outfile_basename
        tmpel.append(tmpname)

        if not out_size is None:
            tmpsize = ET.Element("filesize")
            tmpsize.text = str(out_size)
            tmpel.append(tmpsize)

        #Note extraction errors
        errstr = None
        if rc != 0:
            errstr = "Error extracting file %r; see %r." % (fi.filename(), outfile_abspath + ".err.log")
        elif checksum_match == False:
            errstr = "Checksum mismatch between the original recorded SHA-1 and the extracted file: %r." % fi.filename()
        if not errstr is None:
            logging.error(errstr)
            tmperr = ET.Element("error")
            tmperr.text = errstr
            tmpel.append(tmperr)

        if not out_sha1 is None:
            tmpsha1 = ET.Element("hashdigest")
            tmpsha1.attrib["type"] = "sha1"
            tmpsha1.text = out_sha1
            tmpel.append(tmpsha1)

        tmpchild = copy.copy(fi.xml_element)
        tmpchild.tag = "delta:original_fileobject"
        tmpel.append(tmpchild)

        xoutfh.write(dfxml.ET_tostring(tmpel, encoding="unicode"))
        xoutfh.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find registry files in imagefile and dump hives to files in pwd in the order they're encountered, with a manifest printed to stdout.")
    parser.add_argument("-d", "--debug", help="Enable debug-level logging.", action="store_true")
    parser.add_argument("-x", "--xml", dest="dfxml_file_name", help="Already-created DFXML file for imagefile")
    parser.add_argument("imagefilename", help="Image file")
    args = parser.parse_args()

    if args.dfxml_file_name is None:
        raise ValueError("Sorry, but pre-processed DFXML is not optional at this time.  Please supply an --xml parameter.")

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    imagefile = open(os.path.abspath(args.imagefilename), "rb")
    xmlfh = open(args.dfxml_file_name, "rb")

    xoutfh = open("manifest.dfxml", "w")

    metadict = dict()
    metadict["XMLNS_DFXML"] = dfxml.XMLNS_DFXML
    metadict["XMLNS_DELTA"] = dfxml.XMLNS_DELTA
    metadict["program"] = sys.argv[0]
    metadict["version"] = __version__
    metadict["commandline"] = " ".join(sys.argv)
    metadict["imagefile"] = args.imagefilename

    dfxml_head = """\
<?xml version="1.0" encoding="UTF-8"?>
<dfxml
  version="1.0"
  xmlns='%(XMLNS_DFXML)s'
  xmlns:dc='http://purl.org/dc/elements/1.1/'
  xmlns:delta='%(XMLNS_DELTA)s'
  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <metadata>
    <dc:type>Disk Image Extracted-File Manifest</dc:type>
  </metadata>
  <creator>
    <program>%(program)s</program>
    <version>%(version)s</version>
    <execution_environment>
      <command_line>%(commandline)s</command_line>
    </execution_environment>
  </creator>
  <source>
    <image_filename>%(imagefile)s</image_filename>
  </source>
""" % metadict
    dfxml_foot = """\
</dfxml>
"""

    xoutfh.write(dfxml_head)

    for fi in dfxml.iter_dfxml(xmlfh, preserve_elements=True, imagefile=imagefile):
        proc_dfxml(fi)

    xoutfh.write(dfxml_foot)
