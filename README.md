# RegXML Extractor

Converts Windows Registry hives to a descriptive XML format.

The collective software in this project takes a disk image and outputs a set of RegXML files, one per hive extracted from the image.  These hives' RegXML forms are also converted to a SQLite database, assuring the XML is readable by Python.  Errors at any step in this process are verbosely logged.


## Tested environments

This program has been tested in several Unix/Linux environments.  The tested environments are basically:

* CentOS
* Fedora
* OS X
* Ubuntu

To see procedures and specific versions tested, see INSTALL's Testing section.


## Building and installing

See INSTALL.


## Running

Running `regxml_extractor.sh` without arguments provides the available options.  Usage is basically:

    cd results_directory
    regxml_extractor.sh image_file

Output:
* `*.hive` -- Hive files extracted from file system, named in discovery order.
* `manifest.txt` -- A map of the hive names to the disk image and file system path where they were found.
* `linted.txt` -- A convenience list of RegXML files that passed a basic `xmllint` check.
* `*.hive.regxml` -- RegXML produced from the hive of matching number.
* `*.hive.checked.regxml` -- RegXML, pretty-printed and validated by xmllint.
* `out.sqlite` -- SQLite database representing all hives' contents that could be read by `dfxml.py` and `rx_make_database.py`.  Processing errors are captured in a table.  (Run `sqlite3 out.sqlite` and `.schema` to see the tables available.)
* `*.err.log` -- Standard error of the process generating the matching file name.  Be on the lookout for non-0-byte error logs.
* `*.status.log` -- Exit status of the associated process.  '0' is success, anything else is an error.


## Maintenance

Please report issues with Github's [tracker](https://github.com/ajnelson/regxml_extractor/issues).


## References

RegXML is described in the following publication, in which these analysis tools were used:

Alex Nelson, "RegXML: XML conversion of the Windows Registry for forensic processing and distribution," in _Advances in Digital Forensics VIII_, ser. IFIP Advances in Information and Communication Technology, G. Peterson and S. Shenoi, Eds. Springer, 2012.

The M57-Patents scenario analyzed in the above paper can be found at [Digital Corpora](http://digitalcorpora.org/corpora/scenarios/m57-patents-scenario).  If you wish to use RegXML Extractor to analyze this scenario as in the IFIP publication, see the `etc/m57-sequences.txt` file.  Note that you will need to modify that file to supply full paths to where you have the M57 images stored.

This software was formerly housed at:

https://users.soe.ucsc.edu/~ajnelson/research/nelson_ifip12/
