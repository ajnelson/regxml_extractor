#!/usr/bin/env python3

__version__ = "0.0.1"

import logging
import os
import subprocess
import dfxml
import _autotool_vars

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

    def __init__(self, output_root, target_hive=None, target_disk=None, dfxml_to_import=None, pretty=None):
        """
        @param output_root Output root directory.  Must not exist.
        @param target_hive Path to hive file.  Do not also pass target_disk.
        @param target_disk Path to disk image.  Do not also pass target_hive.
        @param dfxml_to_import Optional path to generated disk image DFXML.  Pass with target_disk.
        @param pretty Has xmllint retain pretty-printed XML whenever it checks structure or validation.
        """
        if target_hive is None and target_disk is None:
            raise ValueError("RegXML_Extractor must be called on either a hive file or disk image.")

        self.pretty = pretty

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

        self.conversion_with_hivexml_dir = os.path.join(self.output_root, "conversion_comparisons")
        os.makedirs(self.conversion_with_hivexml_dir)
        self.convert_with_hivexml()

    def import_dfxml(self):
        os.symlink(self.dfxml_to_import, os.path.join(self.dfxml_generation_dir, "fiwalk.dfxml"))

    def import_hive(self):
        os.symlink(self.target_hive, os.path.join(self.hive_extraction_dir, "0.hive"))
        with open(os.path.join(self.hive_extraction_dir, "hive_extraction.dfxml"), "w") as out_log:
            with open(os.path.join(self.hive_extraction_dir, "hive_extraction.dfxml.err.log"), "w") as err_log:
                cmd = [
                  _autotool_vars.python2,
                  os.path.join(_autotool_vars.pkgdatadir, "python", "dfxml_tool.py"),
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
                logging.debug(cmd)
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
                rc = subprocess.call(
                  cmd,
                  stdout=pretty_output,
                  stderr=linting_log
                )
            with open(log_prefix + ".linted.log", "w") as linted_log:
                linted_log.write(str(rc))

    def extract_hives(self):
        #TODO
        pass

    def convert_with_libhivex(self):
        pass

    def convert_with_hivexml(self):
        pass

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
        RegXML_Extractor(args_all.output_root, target_disk=args_all.disk_image, dfxml_to_import=args_all.import_dfxml, pretty=args_all.pretty)
    elif args_all.command == "analyze_hive":
        RegXML_Extractor(args_all.output_root, target_hive=args_all.hive_file)
