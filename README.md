# RegXML Extractor

Converts Windows Registry hives to a descriptive XML format.

The collective software in this project takes a disk image and outputs a set of RegXML files, one per hive extracted from the image.  These hives' RegXML forms are also converted from RegXML to a SQLite database.

## Building regxml_extractor

To build from the tarball:
    ./configure && make install
(As these are scripts, there isn't much need for `make`.)

To build from upstream (Git):
    ./bootstrap.sh
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

## Tested environments

This program has been tested in the following environments:

* Fedora Core 16 (TODO)
* Ubuntu 12.04

## Dependencies

This program depends on The Sleuth Kit, Fiwalk, Python, Hivex and libxml2.

Also, in Ubuntu, compilation and installation from tarballs requires a path augmentation for Hivex and Fiwalk.  The Python in regxml_extractor require DFXML, which is easiest to satisfy with a path augmentation.  Append this to your shell's .rc file (e.g. .bashrc for Bash):

    export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
    export PYTHONPATH="$SLEUTHKIT_SRC_DIR/tools/fiwalk/python:$PYTHONPATH"

(Where `$SLEUTHKIT_SRC_DIR` is where you choose to extract the zip or Git source for The Sleuth Kit, noted below.)

Package summary: all of the following packages will need to be installed (software that require these are noted below):

* Fedora Core 16: automake python-dateutil gcc libxml2-devel python-devel gcc-c++ libtool java-1.7.0-openjdk-devel openssl-devel
* Ubuntu 12:04: automake libxml2-dev python-dev g++ libtool openjdk-7-jdk libxml2-utils

For development or building from Git, these packages are also necessary:

* Fedora Core 16: TODO
* Ubuntu 12:04: git libtool autopoint ocaml autoconf python-dateutil gettext

### Hivex

A version of Hivex that generates RegXML can be found [here](https://github.com/ajnelson/hivex.git), in the branch 'nelson_ifip12'.  Package dependencies are equivalent to the [upstream hivex](https://github.com/libguestfs/hivex.git).

Git source can be retrieved with:
    git clone https://github.com/ajnelson/hivex.git
    cd hivex
    git checkout nelson_ifip12

To build hivex, you must have the following packages installed (assuming a default environment for the named distros):

* Fedora Core 16: gcc libxml2-devel python-devel
* Ubuntu 12.04: libxml2-dev python-dev

To build from tarballs, run from the extracted source directory:
    ./configure && make && sudo make install
(`./configure --prefix=foo` does not work, unfortunately; but if you do not have sudo rights, the hivexml program can be executed in-place from xml/hivexml.)

To build from Git source, also include these packages:

* Fedora Core 16: git libtool gettext-devel autopoint ocaml automake
* Ubuntu 12.04: git libtool autopoint ocaml autoconf python-dateutil gettext

Compilation from Git includes an extra command:
    ./autogen.sh && ./configure && make && sudo make install

### Fiwalk and The Sleuth Kit

To install Fiwalk, compile The Sleuth Kit provided [here](https://github.com/kfairbanks/sleuthkit/tree/FIwalk_dev) (note the branch `FIwalk_dev`).  The Github tag '[sleuthkit-fiwalk-v1.zip](https://github.com/kfairbanks/sleuthkit/zipball/sleuthkit-fiwalk-v1)' provides a zip archive which we describe building below.

Git source can be retrieved with:
    git clone https://github.com/kfairbanks/sleuthkit.git
    cd sleuthkit
    git checkout sleuthkit-fiwalk-v1
regxml_extractor is tested with tag `sleuthkit-fiwalk-v1`; the `FIwalk-dev` branch can be used if more recent (`git checkout FIwalk_dev`).

This Fiwalk, embedded in The Sleuth Kit, has a dependency on Java (javac in particular), which can be satisfied with the Oracle Java Development Kit (JDK) RPM, or the openjdk package noted below.

* Fedora Core 16: gcc-c++ libtool java-1.7.0-openjdk-devel openssl-devel
* Ubuntu 12.04: g++ libtool openjdk-7-jdk

To compile from the zip archive or Git, run:
    ./bootstrap && ./configure && make && sudo make install

## xmllint

We use the version supplied by package manager:

* Fedora Core 16: TODO
* Ubuntu 12.04: libxml2-utils

## References

RegXML is described in the following publication, in which these analysis tools were used:

Alex Nelson, "RegXML: XML conversion of the Windows Registry for forensic processing and distribution," in _Advances in Digital Forensics VIII, to appear Summer 2012_, ser. IFIP Advances in Information and Communication Technology, G. Peterson and S. Shenoi, Eds. Springer, 2012.

The software here was formerly housed at:

https://users.soe.ucsc.edu/~ajnelson/research/nelson_ifip12/
