#!/bin/bash

set -e
set -x

#Assume Debian
#TODO Add a check

#Below the 'automake' line are "devel" packages, but we'll break that out after the Hivex revisions are upstream.
sudo apt-get install \
  automake  \
  g++ \
  libssl-dev \
  libtool \
  libxml2-dev \
  libxml2-utils \
  make \
  pkg-config \
  python-dev \
  python3 \
  sqlite3 \
  autoconf \
  autopoint \
  gettext \
  libtool \
  ocaml \
  python-dateutil
