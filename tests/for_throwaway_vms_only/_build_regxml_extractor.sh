#!/bin/bash

# NB: This script modifies your bashrc without remorse.  It is only meant for testing on a throwaway VM that has a network connection and git installed.
#
# This script is not meant to be called directly.  Call via one of the similarly-named scripts, appropriate to the distro you are testing.

if [ "x$INSTALL_DEPS" == "x" ]; then
  echo "This script is not meant to be called directly.  Use the appropriate build_on....sh script for your distro." >&2
  exit 1
fi

#One-liner c/o http://stackoverflow.com/a/246128/1207160
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -e
set -x

pushd "$SCRIPTDIR/../.."
if [ $(echo "$PATH" | grep "$HOME/local" | wc -l) -lt 1 ]; then
  echo "~/local did not appear in your PATH, so this test will fail.  Modify your environment (e.g. with \`. "$SCRIPTDIR/../../deps/bashrc"\`) and re-run."
  exit 1
fi
"deps/$INSTALL_DEPS"
git submodule init
git submodule update
deps/build_submodules.sh local
./bootstrap.sh
./configure --prefix=$HOME/local
make
make install
regxml_extractor.sh -h
hivexml deps/hivex/images/minimal
hivexml deps/hivex/images/large
popd
