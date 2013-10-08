#!/bin/bash

set -e
set -x

#Ensure the dfxml.py and fiwalk.py files exist (they're symlinks in Git)
if [ -L "lib/dfxml.py" -a ! -e "lib/dfxml.py" ] || [ -L "lib/fiwalk.py" -a ! -e "lib/fiwalk.py" ]; then
  if [ ! -d ".git" ]; then
    echo "At least one of the symbolic links in lib/ is broken.  To correct this, please supply copies of these files.  You can use 'git clone https://github.com/simsong/dfxml.git' to fetch up-to-date versions." >&2
    exit 1
  else
    echo "Initializing DFXML repository"
    git submodule init deps/dfxml
    git submodule update deps/dfxml
  fi
fi

#Ensure Hivex and its Gnulib is checked out
if [ ! -r "deps/hivex/.gnulib/README" ]; then
  if [ ! -x "deps/hivex/autogen.sh" ]; then
    git submodule init deps/hivex
    git submodule sync deps/hivex
    git submodule update deps/hivex
  fi
  pushd deps/hivex
  ./bootstrap
  popd
fi

if [ ! -r "deps/sleuthkit/Makefile.in" ]; then
  if [ ! -r "deps/sleuthkit/bootstrap" ]; then
    git submodule init deps/sleuthkit
    git submodule sync deps/sleuthkit
    git submodule update deps/sleuthkit
  fi
  pushd deps/sleuthkit
  ./bootstrap
  popd
fi

aclocal
automake --add-missing
autoreconf -i
