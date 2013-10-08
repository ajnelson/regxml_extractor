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
if [ ! -x "deps/hivex/autogen.sh" ]; then
  git submodule init deps/hivex
  git submodule sync deps/hivex
  git submodule update deps/hivex
fi

#Ensure the RegXML Schema is checked out
if [ ! -r "deps/regxml_schema/regxml.xsd" ]; then
  git submodule init deps/regxml_schema
  git submodule sync deps/regxml_schema
  git submodule update deps/regxml_schema
fi

aclocal
automake --add-missing
autoreconf -i
