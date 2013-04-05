#!/bin/bash

if [ ! -r /etc/fedora-release ]; then
  echo "This does not appear to be a Fedora machine." >&2
  exit 1
fi

set -e
set -x

sudo yum install \
  gcc \
  gcc-c++ \
  libtool \
  libxml2-devel \
  openssl-devel \
  python-dateutil \
  python-devel \
#Below this line are "devel" packages, but we'll break that out after the Hivex revisions are upstream.
  automake \
  gettext-devel \
  libtool \
  ocaml
