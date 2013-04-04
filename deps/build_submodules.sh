#!/bin/bash

get_abspath() {
  python -c 'import os,sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$1"
}

case $1 in
  local )
    MAKEINSTALL="make install"
    if [ -z "$2" ]; then
      INSTALLDIR=$HOME/local
    else
      INSTALLDIR=$(get_abspath "$2")
    fi
    ;;
  system )
    MAKEINSTALL="sudo make install"
    INSTALLDIR=/usr/local
    ;;
  * )
    echo "Error: Arguments must be 'local [opt. prefix_dir]', or 'system'" >&2
    exit 1
    ;;
esac

#Halt on any error
set -e
set -v

#One-liner c/o http://stackoverflow.com/a/246128/1207160
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd $SCRIPTDIR/sleuthkit
(./bootstrap && ./configure --prefix="$INSTALLDIR" && make -j && $MAKEINSTALL) || exit 1
popd

pushd $SCRIPTDIR/hivex
(./autogen.sh && ./configure --disable-ruby --disable-python --prefix="$INSTALLDIR" && make -j && $MAKEINSTALL) || exit 1
popd
