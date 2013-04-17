#!/bin/bash

if [ ! -r /etc/centos-release ]; then
  echo "This does not appear to be a Centos machine." >&2
  exit 1
fi

p3=`which python3`
if [ ! -x "$p3" ]; then
  echo "Centos 6.4 does not package Python 3.  You must install it from source."
  echo "  Reference:  http://www.hosting.com/support/linux/installing-python-3-on-centosredhat-5x-from-source" >&2
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
