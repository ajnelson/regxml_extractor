# RegXML Extractor

Converts Windows Registry hives to a descriptive XML format.

The collective software in this project takes a disk image and outputs a set of RegXML files, one per hive extracted from the image.  These hives' RegXML forms are also converted from RegXML to a SQLite database.

## Building

To build from the tarball:
    ./configure && make install
(As these are scripts, there isn't much need for `make`.)

To build as from upstream:
    ./bootstrap
    ./configure && make install

## Running

    cd results_directory
    regxml_extractor.sh image_file

Output:
* `*.hive` --- Hive files extracted from file system.
* `*.hive.regxml` --- RegXML produced from the hive of matching number.
* `*.hive.checked.regxml` --- RegXML, pretty-printed and validated by xmllint.
* `out.sqlite` --- SQLite database representing all hives' contents that could be read by `dfxml.py` and `rx_make_database.py`.
* `*.err.log` --- Standard error of the process generating the matching file name.  Be on the lookout for non-0-byte error logs.
If you don't want to install the scripts, you can run the above from the extracted source directory.

## Dependencies

This program depends on The Sleuth Kit, Fiwalk, Python, Hivex and libxml2.

To install hivex, you must have the following packages installed (assuming a default environment for the named distros):

Fedora 16: gcc libxml2-devel python-devel

Ubuntu 12.04: libxml2-dev python-dev

A version of Hivex that generates RegXML can be found [here](https://github.com/ajnelson/hivex/tree/nelson_ifip12) (note the branch `nelson_ifip12`).

To install Fiwalk, compile The Sleuth Kit provided [here](https://github.com/kfairbanks/sleuthkit/tree/FIwalk_dev) (note the branch `FIwalk_dev`).

This Fiwalk, embedded in The Sleuth Kit, has a dependency on Java (javac in particular), which can be satisfied with the Oracle Java Development Kit (JDK) RPM.

Your environment's PYTHONPATH variable must include the Fiwalk python directory, which would be under:
    <sleuthkit directory>/tools/fiwalk/python
This is to include an udpated dfxml.py.

## References

RegXML is described in the following publication, in which these analysis tools were used:

Alex Nelson, "RegXML: XML conversion of the Windows Registry for forensic processing and distribution," in _Advances in Digital Forensics VIII, to appear Summer 2012_, ser. IFIP Advances in Information and Communication Technology, G. Peterson and S. Shenoi, Eds. Springer, 2012.

The software here was formerly housed at:

https://users.soe.ucsc.edu/~ajnelson/research/nelson_ifip12/
