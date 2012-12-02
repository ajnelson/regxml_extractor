# Installing RegXML Extractor

This document details how to build RegXML Extractor (RE)'s dependent software.

## Building `regxml_extractor`

To build from the tarball:

    ./configure && make && sudo make install

To build from upstream (Git):

    ./bootstrap.sh
    ./configure && make && make install

If `./bootstrap` or `./configure` do not work for lack of dependencies, refer to the detailed dependency building section.

The Git repository includes the expected versions of the DFXML library, Hivex, The Sleuth Kit, and Fiwalk.  Instead of running the Git clones below, you can instead run these commands from the `regxml_extractor` cloned source directory:

    git submodule init
    git submodule update

You can then find Hivex, TSK with Fiwalk, and DFXML in the `deps/` directory.

### OS X

We have built RegXML Extractor on fresh instances of OS X Lion (10.7.5) and Snow Leopard Server (10.6.8) by installing from the source websites:

* XCode (AppStore in Lion, Apple Developer Site for Snow Leopard)
* MacPorts (macports.org)
* Git (git-scm.com) (just needed for Snow Leopard)

In Lion, XCode 4.3.3 requires the command line tools (which include `gcc` and `git`) be installed through XCode's Preferences -> Downloads -> Components -> Command Line Tools.

## Building and installing dependencies

This program depends on The Sleuth Kit, Fiwalk, Python 3, Hivex, DFXML, and libxml2.

Also, in Ubuntu, compilation and installation from tarballs requires a path augmentation for Hivex and Fiwalk.

    export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"

The Sleuth Kit can link against libewf.  For example, in OS X, adding these paths let a locally-built TSK link against the MacPorts-installed libewf:

    export LIBRARY_PATH="/opt/local/lib:$LIBRARY_PATH"
    export LD_LIBRARY_PATH="/opt/local/lib:$LD_LIBRARY_PATH"
    export C_INCLUDE_PATH="/opt/local/include:$C_INCLUDE_PATH"
    export CPLUS_INCLUDE_PATH="/opt/local/include:$CPLUS_INCLUDE_PATH"

In Linux, `/usr` replaces `/opt`.

### Package summary

All of the following packages will need to be installed (software that require these are noted below):

* Fedora Core 16, 17: python-dateutil gcc libxml2-devel python-devel gcc-c++ libtool java-1.7.0-openjdk-devel openssl-devel
* Ubuntu 12:04: automake libxml2-dev python-dev g++ libtool openjdk-7-jdk libxml2-utils libssl-dev
* OS X 10.6.8 Server MacPorts: ocaml pkgconfig getopt
* OS X 10.7.4 Desktop MacPorts: automake autoconf libtool ocaml pkgconfig getopt

For development or building from Git, these packages are also necessary:

* Fedora Core 16: git libtool gettext-devel autopoint ocaml automake
* Fedora Core 17: git libtool gettext-devel ocaml automake
* Ubuntu 12:04: git libtool autopoint ocaml autoconf python-dateutil gettext
* OS X 10.6.8 Server MacPorts: (Nothing more needed)
* OS X 10.7.4 Desktop MacPorts: (Nothing more needed)

### Hivex

A version of Hivex that generates RegXML can be found [here](https://github.com/ajnelson/hivex.git), in the branch '`regxml`'.  Package dependencies are equivalent to the [upstream hivex](https://github.com/libguestfs/hivex.git).

Building in OS X is a slight bit trickier.  You can skip to the OS X subsection and ignore the Linux instructions.

To build hivex from a tarball, you must have the following packages installed (assuming a default environment for the named distros):

* Fedora Core 16, 17: gcc libxml2-devel python-devel
* Ubuntu 12.04: libxml2-dev python-dev
* OS X: (see OS X section)

With those prerequisites installed, run the normal building commands from the extracted source directory:

    ./configure --prefix=foo && make && sudo make install

(Due to a build quirk, to use `./configure --prefix=foo', you must also pass `--disable-python' to `./configure'.)

#### Hivex from Git

To build from Git source, also include these packages:

* Fedora Core 16: git libtool gettext-devel autopoint ocaml automake
* Fedora Core 17: git libtool gettext-devel ocaml automake
* Ubuntu 12.04: git libtool autopoint ocaml autoconf python-dateutil gettext
* OS X: (see OS X section)

Git source can be retrieved with:

    git clone --branch=nelson_ifip12 https://github.com/ajnelson/hivex.git

Compilation from Git starts with an extra command:

    ./autogen.sh && ./configure && make && sudo make install

#### OS X and Hivex

If building in Snow Leopard or Lion, you must build from Git, in a particular version that works around an issue specific to OS X.  Retrieve the source with:

    git clone https://github.com/ajnelson/hivex.git
    cd hivex
    git checkout regxml_osx

These ports are needed in OS X:

* OS X 10.6.8 Server MacPorts: ocaml pkgconfig (see section on Snow Leopard and pkgconfig)
* OS X 10.7.4 Desktop MacPorts: autoconf automake libtool ocaml pkgconfig

In OS X, there is an error compiling the Ruby binaries, including at least Hivex versions 1.3.1 and 1.3.6.  To bypass the error, pass `--disable-ruby` to `./configure`:

    ./autogen.sh && ./configure --disable-ruby && make && sudo make install

#### OS X Snow Leopard, Hivex and pkgconfig

The Snow Leopard MacPort of `pkg-config` does not integrate automatically with GNU Autotools on installation with `port`; the `pkg.m4` macro file is stored outside the `ACLOCAL_PATH`.  One solution to this issue is running the following command (thanks to Jim Meyering for the tip) after installing pkgconfig:

    sudo bash -c "printf '%s/share/aclocal\n' /opt/local /usr >>$(aclocal --print-ac-dir)/dirlist"

Note that if you installed `pkg-config` in Snow Leopard and upgraded to Lion, this issue persists through the upgrade.

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

* Fedora Core 16, 17: gcc-c++ libtool java-1.7.0-openjdk-devel openssl-devel
* Ubuntu 12.04: g++ libtool openjdk-7-jdk autoconf automake libssl-dev
* OS X 10.6.8 Server MacPorts: (Nothing in addition to XCode needed)
* OS X 10.7.4 Desktop MacPorts: autoconf automake libtool; and java: To install Java, invoking `java` launches an installer if the runtime environment's absent

To compile from the zip archive or Git, run:

    ./bootstrap && ./configure && make && sudo make install

