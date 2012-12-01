#!/bin/bash

if [ -z "$prefix" ]; then
  prefix=$HOME/local
fi

#One-liner c/o http://stackoverflow.com/a/246128/1207160
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd $SCRIPTDIR/hivex
(./autogen.sh && ./configure --disable-ruby --disable-python --prefix="$prefix" && make -j && make install) || exit 1
popd

pushd $SCRIPTDIR/sleuthkit
(./bootstrap && ./configure --prefix="$prefix" && make -j && make install) || exit 1
popd
