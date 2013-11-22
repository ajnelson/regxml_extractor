#!/bin/bash

get_abspath() {
  python -c 'import os,sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$1"
}

#OS X needs a few tweaks to running Hivex's ./configure
#TODO At least OS X 10.8 needs it.  10.7 and 10.9 might too.  Check.
hivex_configure_extra_flags=
if [ ! -z "$RE_HIVEX_CONFIGURE_EXTRA_FLAGS" ]; then
  hivex_configure_extra_flags="$RE_HIVEX_CONFIGURE_EXTRA_FLAGS"
else
  if [ "x$(uname -s)" == "xDarwin" ]; then
    echo "$0: Error: On OS X 10.8, this script needs an extra environment variable passed in, \$RE_HIVEX_CONFIGURE_EXTRA_FLAGS." >&2
    exit 1
  fi
fi

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
(./bootstrap && ./configure --disable-java --prefix="$INSTALLDIR" && make -j && $MAKEINSTALL) || exit 1
popd

pushd $SCRIPTDIR/hivex
(./autogen.sh && ./configure --disable-ruby --disable-python --prefix="$INSTALLDIR" $hivex_configure_extra_flags && make -j && $MAKEINSTALL) || exit 1
popd
