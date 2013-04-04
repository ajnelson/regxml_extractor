#!/bin/bash

if [ ! -x `which port` ]; then
  echo "\`port' not found. Download and install MacPorts." >&2
  exit 1
fi

set -e
set -x

sudo port install \
    autoconf \
    automake \
    libtool
#    getopt \
#    ocaml \
#    pkgconfig
