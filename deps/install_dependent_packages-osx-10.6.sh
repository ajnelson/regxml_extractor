#!/bin/bash

if [ ! -x `which port` ]; then
  echo "Error: \`port' not found. Download and install MacPorts." >&2
  exit 1
fi

set -e
set -x

#TODO 10.6.8 server only needed ocaml, pkgconfig, getopt in prior testing; check again.
sudo port selfupdate
sudo port install \
  autoconf \
  automake \
  getopt \
  libtool \
  ocaml \
  pkgconfig \
  python33

#Thanks to Jim Meyering for the dirlist tip for dealing with PKG_CHECK_MODULES not being found.
PKGM4=$(find /opt/local /usr -name 'pkg.m4' | head -n1 2>/dev/null)
if [ ! -r "$PKGM4" ]; then
  echo "Error: pkg.m4 file not found; hivex will fail to build." >&2
  exit 1
fi
ACLOCALDIRLIST=$(aclocal --print-ac-dir)/dirlist
if [ ! -r "$ACLOCALDIRLIST" -o ! $(grep "$(dirname "$PKGM4")" "$ACLOCALDIRLIST" | wc -l) -gt 0 ]; then
  echo "Note: Augmenting aclocal path with m4 directories." >&2
  sudo bash -c "printf '%s/share/aclocal\n' /opt/local /usr >>$(aclocal --print-ac-dir)/dirlist"
fi
test $(grep 'pkg.m4' $(aclocal --print-ac-dir)/dirlist | wc -l) -gt 0 ;
