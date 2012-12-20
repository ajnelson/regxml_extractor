#!/bin/bash

set -e
set -v

if [ -r /etc/fedora-release ]; then
  #Assume Fedora
  sudo yum install \
    gcc \
    gcc-c++ \
    java-1.7.0-openjdk-devel \
    libtool \
    libxml2-devel \
    openssl-devel \
    python-dateutil \
    python-devel
else #TODO
  #Assume Ubuntu
  sudo apt-get install \
    automake  \
    g++ \
    libssl-dev \
    libtool \
    libxml2-dev \
    libxml2-utils \
    openjdk-7-jdk \
    python-dev
else #TODO
  #Assume Mac OS X
  sudo port install \
    autoconf  \
    automake \
    getopt \
    libtool \
    ocaml \
    pkgconfig
  #TODO 10.6.8 server only needed ocaml, pkgconfig, getopt; check for OS version.
fi

### Package summary

For development or building from Git, these packages are also necessary:

* Fedora Core 16: git libtool gettext-devel autopoint ocaml automake
* Fedora Core 17: git libtool gettext-devel ocaml automake
* Ubuntu 12:04: git libtool autopoint ocaml autoconf python-dateutil gettext
* OS X 10.6.8 Server MacPorts: (Nothing more needed)
* OS X 10.7.4 Desktop MacPorts: (Nothing more needed)


