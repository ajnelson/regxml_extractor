# RegXML Extractor

Converts Windows Registry hives to a descriptive XML format.

The collective software in this project takes a disk image and outputs a set of RegXML files, one per hive extracted from the image.  These hives' RegXML forms are also converted from RegXML to a SQLite database.

## Tested environments

This program has been tested in the following environments:

* Fedora Core 16
* Ubuntu 12.04

## Building `regxml_extractor`

To build from the tarball:

    ./configure && make install

(As this package only contains scripts, there isn't much need for `make`.)

To build from upstream (Git):

    ./bootstrap.sh
    ./configure && make install

The Git repository includes the expected versions of Hivex, The Sleuth Kit and Fiwalk.  Instead of running the Git clones below, you can instead run these commands from the `regxml_extractor` cloned source directory:

    git submodule init
    git submodule update

You can then find Hivex, TSK with Fiwalk, and DFXML in the `deps/` directory.

### OS X

We have built RegXML Extractor on fresh instances of OS X Lion (10.7.4) and Snow Leopard Server (10.6.8) by installing from the source websites:

* XCode (AppStore in Lion, Apple Developer Site for Snow Leopard)
* MacPorts (macports.org)
* Git (git-scm.com) (just needed for Snow Leopard)

In Lion, XCode 4.3.3 requires the command line tools (which include `gcc` and `git`) be installed through XCode's Preferences -> Downloads -> Components -> Command Line Tools.

## Running

    cd results_directory
    regxml_extractor.sh image_file

Output:
* `*.hive` -- Hive files extracted from file system, named in discovery order.
* `manifest.txt` -- A map of the hive names to the disk image and file system path where they were found.
* `*.hive.regxml` -- RegXML produced from the hive of matching number.
* `*.hive.checked.regxml` -- RegXML, pretty-printed and validated by xmllint.
* `out.sqlite` -- SQLite database representing all hives' contents that could be read by `dfxml.py` and `rx_make_database.py`.  Processing errors are captured in a table.  (Run `sqlite3 out.sqlite` and `.schema` to see the tables available.)
* `*.err.log` -- Standard error of the process generating the matching file name.  Be on the lookout for non-0-byte error logs.

If you don't want to install the scripts, you can run the above from the extracted source directory.

## Dependencies

This program depends on The Sleuth Kit, Fiwalk, Python, Hivex and libxml2.

Also, in Ubuntu, compilation and installation from tarballs requires a path augmentation for Hivex and Fiwalk.

    export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"

The Python in `regxml_extractor` requires DFXML, which is easiest to satisfy with a path augmentation.  Append this to your shell's `.rc` file (e.g. `.bashrc` for Bash):

    export PYTHONPATH="$REGXML_EXTRACTOR_SRC_DIR/lib:$PYTHONPATH"

(Where `$REGXML_EXTRACTOR_SRC_DIR` is the directory with this README.)

The Sleuth Kit can link against libewf.  For example, in OS X, adding these paths let a locally-built TSK link against the MacPorts-installed libewf:

    export LIBRARY_PATH="/opt/local/lib:$LIBRARY_PATH"
    export LD_LIBRARY_PATH="/opt/local/lib:$LD_LIBRARY_PATH"
    export C_INCLUDE_PATH="/opt/local/include:$C_INCLUDE_PATH"
    export CPLUS_INCLUDE_PATH="/opt/local/include:$CPLUS_INCLUDE_PATH"

In Linux, `/usr` replaces `/opt`.

### Package summary

All of the following packages will need to be installed (software that require these are noted below):

* Fedora Core 16: automake python-dateutil gcc libxml2-devel python-devel gcc-c++ libtool java-1.7.0-openjdk-devel openssl-devel
* Ubuntu 12:04: automake libxml2-dev python-dev g++ libtool openjdk-7-jdk libxml2-utils
* OS X 10.6.8 Server MacPorts: TODO
* OS X 10.7.4 Server MacPorts: TODO

For development or building from Git, these packages are also necessary:

* Fedora Core 16: git libtool gettext-devel autopoint ocaml automake
* Ubuntu 12:04: git libtool autopoint ocaml autoconf python-dateutil gettext
* OS X 10.6.8 Server MacPorts: ocaml pkgconfig
* OS X 10.7.4 Desktop MacPorts: TODO
LION TODO INSTALLED: automake autoconf ocaml pkgconfig libtool
LION TODO NOT YET INSTALLED: libxml2-devel python-devel openssl-devel

### Hivex

A version of Hivex that generates RegXML can be found [here](https://github.com/ajnelson/hivex.git), in the branch '`regxml`'.  Package dependencies are equivalent to the [upstream hivex](https://github.com/libguestfs/hivex.git).

Building in OS X is a slight bit trickier.  Please read this section and the following subsections on OS X before proceeding.

Git source can be retrieved with:

    git clone https://github.com/ajnelson/hivex.git
    cd hivex
    git checkout nelson_ifip12

To build hivex, you must have the following packages installed (assuming a default environment for the named distros):

* Fedora Core 16: gcc libxml2-devel python-devel
* Ubuntu 12.04: libxml2-dev python-dev
* OS X: (see OS X section)

To build from tarballs, run from the extracted source directory:

    ./configure && make && sudo make install

(`./configure --prefix=foo` does not work, unfortunately; but if you do not have `sudo` rights, the `hivexml` program can be executed in-place from `xml/hivexml`.)

To build from Git source, also include these packages:

* Fedora Core 16: git libtool gettext-devel autopoint ocaml automake
* Ubuntu 12.04: git libtool autopoint ocaml autoconf python-dateutil gettext
* OS X: (see OS X section)

Compilation from Git includes an extra command:

    ./autogen.sh && ./configure && make && sudo make install

#### OS X and Hivex

If building in Snow Leopard or Lion, you must build from Git, in a particular version that works around an issue specific to OS X.  Retrieve the source with:

    git clone https://github.com/ajnelson/hivex.git
    cd hivex
    git checkout regxml_osx

These ports are needed in OS X:

* OS X 10.6.8 Server MacPorts: ocaml pkgconfig (see section on Snow Leopard and pkgconfig)
* OS X 10.7.4 Desktop MacPorts: ocaml

In OS X, there is an error compiling the Ruby binaries, including at least Hivex versions 1.3.1 and 1.3.6.  To bypass the error, pass `--disable-ruby` to `./configure`:

    ./autogen.sh && ./configure --disable-ruby && make && sudo make install

#### OS X Snow Leopard, Hivex and pkgconfig

The Snow Leopard MacPort of `pkg-config` does not integrate automatically with GNU Autotools on installation with `port`; the `pkg.m4` macro file is stored outside the `ACLOCAL_PATH`.  One solution to this issue is running the following command (thanks to Jim Meyering for the tip) after installing pkgconfig:

    sudo bash -c "printf '%s/share/aclocal\n' /opt/local /usr >>$(aclocal --print-ac-dir)/dirlist"

#### Hivex language bindings (optional)

To use all the language bindings bundled with Hivex, install these packages:

* Fedora Core 16: perl-devel perl-Test-Simple perl-Test-Pod perl-Test-Pod-Coverage perl-ExtUtils-MakeMaker perl-IO-stringy perl-libintl ruby-devel rubygem-rake ocaml-findlib-devel readline-devel
* Ubuntu 12.04: (Not tested)
* OS X 10.7 Desktop MacPorts: (Not tested)
* OS X 10.6.8 Server MacPorts: (Not tested)

### Fiwalk and The Sleuth Kit

To install Fiwalk, compile The Sleuth Kit provided [here](https://github.com/kfairbanks/sleuthkit/tree/FIwalk_dev) (note the branch `FIwalk_dev`).  The Github tag '[sleuthkit-fiwalk-v1.zip](https://github.com/kfairbanks/sleuthkit/zipball/sleuthkit-fiwalk-v1)' provides a zip archive which we describe building below.

Git source can be retrieved with:

    git clone https://github.com/kfairbanks/sleuthkit.git
    cd sleuthkit
    git checkout sleuthkit-fiwalk-v1

RegXML Extractor is tested with tag `sleuthkit-fiwalk-v1`; the `FIwalk-dev` branch can be used if more recent (`git checkout FIwalk_dev`).

This Sleuth Kit has a dependency on Java (javac in particular), which can be satisfied with the Oracle Java Development Kit (JDK) RPM, or the openjdk package noted below.

* Fedora Core 16: gcc-c++ libtool java-1.7.0-openjdk-devel openssl-devel
* Ubuntu 12.04: g++ libtool openjdk-7-jdk
* OS X 10.6.8: (Nothing in addition to XCode needed)
* OS X 10.7 Desktop MacPorts: autoconf automake libtool; and java: To install Java, invoking `java` launches an installer if the runtime environment's absent

To compile from the zip archive or Git, run:

    ./bootstrap && ./configure && make && sudo make install

### xmllint

We use the version supplied by package managers:

* Fedora Core 16: (already installed)
* Ubuntu 12.04: libxml2-utils
* OS X 10.7: (already installed)
* OS X 10.6.8: TODO libxml2? (seems to be installed as ocaml dependency)

## Maintenance

Please report issues with Github's [tracker](https://github.com/ajnelson/regxml_extractor/issues).

## References

RegXML is described in the following publication, in which these analysis tools were used:

Alex Nelson, "RegXML: XML conversion of the Windows Registry for forensic processing and distribution," in _Advances in Digital Forensics VIII, to appear Summer 2012_, ser. IFIP Advances in Information and Communication Technology, G. Peterson and S. Shenoi, Eds. Springer, 2012.

The M57-Patents scenario analyzed in the above paper can be found at [Digital Corpora](http://digitalcorpora.org/corpora/scenarios/m57-patents-scenario).  If you wish to use RegXML Extractor to analyze this scenario as in the IFIP publication, see the `etc/m57-sequences.txt` file.  Note that you will need to modify that file to supply full paths to where you have the M57 images stored.

This software was formerly housed at:

https://users.soe.ucsc.edu/~ajnelson/research/nelson_ifip12/
