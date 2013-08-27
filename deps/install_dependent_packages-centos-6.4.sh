#!/bin/bash

if [ ! -r /etc/centos-release ]; then
  echo "This does not appear to be a Centos machine." >&2
  exit 1
fi

#Install sqlite-devel before configuring Python 3
sudo yum install sqlite-devel

p3=`which python3`
if [ ! -x "$p3" ]; then
  echo "Error: Centos 6.4 does not package Python 3.  You must install it from source.  For this test, this command line should be used from the Python tarball:" >&2
  echo "" >&2
  echo "    ./configure --prefix=/usr && make -j && sudo make install" >&2
  echo "" >&2
  echo "  Reference:  http://www.hosting.com/support/linux/installing-python-3-on-centosredhat-5x-from-source" >&2
  exit 1
fi

"$p3" -c 'import sqlite3'
rcpy3sqlite3=$?
if [ ! $rcpy3sqlite3 -eq 0 ]; then
  echo "Error: Python 3 was not configured with SQLite support.  Install 'sqlite-devel' and then re-configure Python 3." >&2
  echo "  Reference:  http://stackoverflow.com/a/2747227" >&2
  exit 1
fi

set -e
set -x

#Below the 'automake' line are "devel" packages, but we'll break that out after the Hivex revisions are upstream.
sudo yum install \
  gcc \
  gcc-c++ \
  libxml2-devel \
  openssl-devel \
  python-dateutil \
  python-devel \
  automake \
  gettext-devel \
  libtool \
  ocaml
