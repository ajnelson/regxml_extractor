#!/bin/bash

if [ -z "$prefix" ]; then
  prefix=$HOME/local
fi

pushd hivex
(./autogen.sh && ./configure && make) || exit 1
popd

pushd sleuthkit
(./bootstrap && ./configure --prefix="$prefix" && make && make install) || exit 1
popd
