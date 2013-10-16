#!/usr/bin/env python3

#TODO Of course, this documentation is out of date since starting this afternoon
"""
Extraction step creates a directory hive_extraction, with contents:

* hive_extraction.dfxml - DFXML excerpts of fiwalk's output.  Each fileobject includes an attribute, regxml:extraction_error="0" (or other exit status).
* $fiwalk_id.hive

New flat RegXML generator conversion step creates a directory conversion_with_libhivex, with contents:

* $fiwalk_id.regxml
* $fiwalk_id.regxml.out.log
* $fiwalk_id.regxml.err.log
* $fiwalk_id.regxml.status.log
* $fiwalk_id.regxml.validation.log
* conversion.dfxml - DFXML that describes each .hivexml and .regxml file in the directory, and the version of xmllint and libhivex used.  Includes original_fileobject.  Each fileobject for a .regxml file includes an attribute, regxml:regxml_validation_error="0" (or other exit status).

Hivexml conversion step creates a directory conversion_with_hivexml, with contents:

* $fiwalk_id.hivexml
* $fiwalk_id.hivexml.err.log
* $fiwalk_id.hivexml.status.log
* $fiwalk_id.hivexml.linting.log
* $fiwalk_id.hivexml.linted.log - Ensures that xmllint will run on it (so the XML is at least well-formed).
* $fiwalk_id.regxml
* $fiwalk_id.regxml.err.log
* $fiwalk_id.regxml.status.log
* $fiwalk_id.regxml.validation.log
* conversion.dfxml - DFXML that describes each .hivexml and .regxml file in the directory, and the version of xmllint and libhivex used.  Includes original_fileobject.  Each fileobject for a .regxml file includes an attribute, regxml:valid_regxml="1|0".  Each fileobject for a .hivexml file includes an attribute, regxml:xmllint_error="0" (or other exit status).

RegXML comparison step creates a directory conversion_comparisons, with contents:
* $fiwalk_id.libhivex_vs_hivexml.txt
* $fiwalk_id.hivexml_vs_libhivex.txt

SQLite conversion step creates a directory as_sqlite, with contents:
* out.sqlite - Created by walking conversion_with_hivexml/conversion.dfxml for successfully linted .hivexml files. (Will be .regxml files when the DFXML library is updated.)
"""

__version__ = "0.0.3"

import logging
import os
import subprocess
import dfxml
import _autotool_vars
import glob
import sys

if sys.version_info.major < 3:
    raise Exception("%r requires Python major version 3." % sys.argv[0])

_dirstack = []
def pushd(dirname):
    global _dirstack
    _dirstack.append(os.curdir)
    os.chdir(dirname)
def popd():
    global _dirstack
    assert(len(_dirstack) > 0)
    os.chdir(_dirstack.pop())

class RegXML_Extractor:
    """
    This class isn't really meant to be a well-modeled object.  It instead maintains some state to break up some function flow, without resorting to module-level variables.
    """

    def __init__(self, output_root, target_hive=None, target_disk=None, dfxml_to_import=None, pretty=None, debug=None, zap=None, path_to_rx_py=None):
        """
        @param output_root Output root directory.  Must not exist.
        @param target_hive Path to hive file.  Do not also pass target_disk.
        @param target_disk Path to disk image.  Do not also pass target_hive.
        @param dfxml_to_import Optional path to generated disk image DFXML.  Pass with target_disk.
        @param pretty Has xmllint retain pretty-printed XML whenever it checks structure or validation.
        @param path_to_rx_py Path to RegXML Extractor Python scripts.  For unit testing.
        """
        if target_hive is None and target_disk is None:
            raise ValueError("RegXML_Extractor must be called on either a hive file or disk image.")

        self.pretty = pretty
        self.debug = debug
        self.zap = zap

        if path_to_rx_py is None:
            self.path_to_rx_py = os.path.join(_autotool_vars.pkgdatadir, "python")
        else:
            self.path_to_rx_py = os.path.abspath(path_to_rx_py)
        logging.debug("path_to_rx_py = %r" % path_to_rx_py)
        logging.debug("self.path_to_rx_py = %r" % self.path_to_rx_py)

        self._mode = None
        if not target_disk is None:
            with open(target_disk, "r") as test_readable:
                pass
            self.target_disk = os.path.abspath(target_disk)
            self._mode = "analyze_disk"

            self.dfxml_to_import = None
            if not dfxml_to_import is None:
                with open(dfxml_to_import, "r") as test_readable:
                    pass
                self.dfxml_to_import = os.path.abspath(dfxml_to_import)

        if not target_hive is None:
            if not self._mode is None:
                raise Exception("RegXML_Extractor must be called on either a hive file or a disk image - not both.")
            with open(target_hive, "r") as test_readable:
                pass
            self.target_hive = os.path.abspath(target_hive)
            self._mode = "analyze_hive"

        self.output_root = os.path.abspath(output_root)
        if os.path.exists(self.output_root) and self.zap:
            import shutil
            shutil.rmtree(self.output_root)
        os.makedirs(self.output_root)

        self.dfxml_generation_dir = os.path.join(self.output_root, "dfxml_generation")
        os.makedirs(self.dfxml_generation_dir)
        if self._mode == "analyze_disk":
            if self.dfxml_to_import:
                self.import_dfxml()
            else:
                self.do_fiwalk_on_disk_image()
            self.check_dfxml()
        elif self._mode == "analyze_hive":
            pass

        self.hive_extraction_dir = os.path.join(self.output_root, "hive_extraction")
        os.makedirs(self.hive_extraction_dir)
        if self._mode == "analyze_disk":
            self.extract_hives()
        elif self._mode == "analyze_hive":
            self.import_hive()

        self.conversion_with_libhivex_dir = os.path.join(self.output_root, "conversion_with_libhivex")
        os.makedirs(self.conversion_with_libhivex_dir)
        self.convert_with_libhivex()

        self.conversion_with_hivexml_dir = os.path.join(self.output_root, "conversion_with_hivexml")
        os.makedirs(self.conversion_with_hivexml_dir)
        self.convert_with_hivexml()

        self.conversion_comparisons_dir = os.path.join(self.output_root, "conversion_comparisons")
        os.makedirs(self.conversion_comparisons_dir)
        self.compare_conversions()

    def import_dfxml(self):
        os.symlink(self.dfxml_to_import, os.path.join(self.dfxml_generation_dir, "fiwalk.dfxml"))

    def import_hive(self):
        os.symlink(self.target_hive, os.path.join(self.hive_extraction_dir, "0.hive"))
        with open(os.path.join(self.hive_extraction_dir, "hive_extraction.dfxml"), "w") as out_log:
            with open(os.path.join(self.hive_extraction_dir, "hive_extraction.dfxml.err.log"), "w") as err_log:
                cmd = [
                  _autotool_vars.python2,
                  os.path.join(self.path_to_rx_py, "dfxml_tool.py"),
                  "--commandline",
                  "--iso-8601",
                  "--md5",
                  "--sha1",
                  "--sha256",
                ]
                pushd(self.hive_extraction_dir)
                for hive_name in glob.glob("*.hive"):
                    cmd.append(hive_name)
                popd()
                logging.debug("cmd = %r" % cmd)
                rc = subprocess.call(
                  cmd,
                  stdout=out_log,
                  stderr=err_log,
                  cwd=self.hive_extraction_dir,
                )
                with open(os.path.join(self.hive_extraction_dir, "hive_extraction.dfxml.status.log"), "w") as status_log:
                    status_log.write(str(rc))

    def do_fiwalk_on_disk_image(self):
        log_prefix = os.path.join(self.dfxml_generation_dir, "fiwalk.dfxml")
        with open(log_prefix + ".out.log", "w") as out_log:
            with open(log_prefix + ".err.log", "w") as err_log:
                rc = subprocess.call(
                  [_autotool_vars.fiwalk, "-O", "-X", "fiwalk.dfxml", self.target_disk],
                  stdout=out_log,
                  stderr=err_log,
                  cwd=self.dfxml_generation_dir
                )
                with open(log_prefix + ".status.log", "w") as status_log:
                    status_log.write(str(rc))
                if rc != 0:
                    raise Exception("Fiwalk failed while processing the disk image.  Aborting.")

    def check_dfxml(self):
        log_prefix = os.path.join(self.dfxml_generation_dir, "fiwalk.dfxml")
        if self.pretty:
            out_path = log_prefix + ".formatted.xml"
        else:
            out_path = "/dev/null"
        with open(out_path, "w") as pretty_output:
            with open(log_prefix + ".linting.log", "w") as linting_log:
                cmd = [
                  _autotool_vars.xmllint,
                  "--format",
                  log_prefix
                ]
                logging.debug("cmd = %r" % cmd)
                rc = subprocess.call(
                  cmd,
                  stdout=pretty_output,
                  stderr=linting_log
                )
                with open(log_prefix + ".linted.log", "w") as linted_log:
                    linted_log.write(str(rc))
                if rc != 0:
                    raise Exception("The DFXML file did not validate.  Aborting.")

    def extract_hives(self):
        #TODO
        pass

    def get_hives_to_analyze(self):
        #TODO Replace this glob with DFXML walk of hive_extraction.dfxml
        retval = []
        pushd(self.hive_extraction_dir)
        for hive_basename in glob.glob("*.hive"):
            retval.append(os.path.join(self.hive_extraction_dir, hive_basename))
        popd()
        return retval

    def convert_with_libhivex(self):
        hive_abs_paths = self.get_hives_to_analyze()

        pushd(self.conversion_with_libhivex_dir)
        for hive_abs_path in hive_abs_paths:
            hive_basename = os.path.basename(hive_abs_path)
            #Basename, no extension
            hive_basename_ne = os.path.splitext(hive_basename)[0]
            hive_id_prefix = os.path.join(self.conversion_with_libhivex_dir, hive_basename_ne)

            #Build command
            cmd = [_autotool_vars.python3, os.path.join(self.path_to_rx_py, "rx_make_flat_regxml.py")]
            if self.debug:
                cmd.append("-d")
            cmd.append(hive_abs_path)
            logging.debug("sys.path = %r" % sys.path)
            logging.debug("cmd = %r" % cmd)

            #Generate RegXML output
            libhivex_file = hive_id_prefix + ".regxml"
            rc_libhivex = None
            with open(libhivex_file, "w") as out_log:
              with open(libhivex_file+ ".err.log", "w") as err_log:
                rc_libhivex = subprocess.call(
                  cmd,
                  stdout=out_log,
                  stderr=err_log
                )
                with open(libhivex_file + ".status.log", "w") as status_log:
                    status_log.write(str(rc_libhivex))
            if rc_libhivex != 0:
                logging.info("Libhivex failed on %r." % hive_abs_path)
                continue
            #TODO Lint and validate output
        popd()

    def convert_with_hivexml(self):
        hive_abs_paths = self.get_hives_to_analyze()

        pushd(self.conversion_with_hivexml_dir)
        for hive_abs_path in hive_abs_paths:
            hive_basename = os.path.basename(hive_abs_path)
            #Basename, no extension
            hive_basename_ne = os.path.splitext(hive_basename)[0]
            hive_id_prefix = os.path.join(self.conversion_with_hivexml_dir, hive_basename_ne)

            #Build command
            cmd = [_autotool_vars.hivexml]
            if self.debug:
                cmd.append("-d")
            cmd.append(hive_abs_path)

            #Generate Hivexml output
            hivexml_file = hive_id_prefix + ".hivexml"
            rc_hivexml = None
            with open(hivexml_file, "w") as out_log:
              with open(hivexml_file + ".err.log", "w") as err_log:
                #TODO Once again, Hivex 1.3.8 fails to compile on OS X.  Need to hunt this down.
                rc_hivexml = subprocess.call(
                  cmd,
                  stdout=out_log,
                  stderr=err_log
                )
                with open(hivexml_file + ".status.log", "w") as status_log:
                    status_log.write(str(rc_hivexml))
            if rc_hivexml != 0:
                logging.info("Hivexml failed on %r.  Skipping RegXML generation." % hive_abs_path)
                continue
            #TODO Lint output

            #Generate RegXML
            regxml_file = hive_id_prefix + ".regxml"
            rc_flattener = None
            with open(regxml_file, "w") as out_log:
              with open(regxml_file + ".err.log", "w") as err_log:
                rc_flattener = subprocess.call(
                  [
                    _autotool_vars.python3,
                    os.path.join(os.path.join(_autotool_vars.pkgdatadir, "python", "flatten_regxml.py")),
                    hivexml_file
                  ],
                  stdout=out_log,
                  stderr=err_log
                )
                with open(regxml_file + ".status.log", "w") as status_log:
                    status_log.write(str(rc_flattener))
            #TODO Validate output
        popd()

    def compare_conversions(self):
        pass

    def convert_to_sqlite(self):
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--pretty", help="Pretty-print XML whenever it is checked with xmllint.", action="store_true")
    parser.add_argument("--import-dfxml", help="Path to pre-generated DFXML file for the disk image.")
    parser.add_argument("--path-to-rx-py", help="Path to RegXML Extractor Python scripts.  For unit testing.")
    parser.add_argument("-Z", "--zap", help="Remove prior output. Use with care.", action="store_true")
    parser.add_argument("command")
    (args_init, args_extra) = parser.parse_known_args()

    if args_init.command == "analyze_hive":
        parser.add_argument("hive_file")
        parser.add_argument("output_root")
    elif args_init.command == "analyze_disk":
        parser.add_argument("disk_image")
        parser.add_argument("output_root")
    else:
        raise ValueError("The command must be one of: analyze_hive, analyze_disk")
    args_all = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args_all.debug else logging.INFO)

    if args_all.command == "analyze_disk":
        RegXML_Extractor(args_all.output_root, target_disk=args_all.disk_image, dfxml_to_import=args_all.import_dfxml, pretty=args_all.pretty, debug=args_all.debug, zap=args_all.zap, path_to_rx_py=args_all.path_to_rx_py)
    elif args_all.command == "analyze_hive":
        RegXML_Extractor(args_all.output_root, target_hive=args_all.hive_file, pretty=args_all.pretty, debug=args_all.debug, zap=args_all.zap, path_to_rx_py=args_all.path_to_rx_py)
