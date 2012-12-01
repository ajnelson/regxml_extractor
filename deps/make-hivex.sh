#!/bin/bash

#Halt on any error
set -e
set -v

if [ -z "$prefix" ]; then
  prefix=$HOME/local
fi

#One-liner c/o http://stackoverflow.com/a/246128/1207160
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd $SCRIPTDIR/sleuthkit
(./bootstrap && ./configure --prefix="$prefix" && make -j && make install) || exit 1
popd

