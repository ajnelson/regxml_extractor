#!/bin/sh

set -e
set -x

#readline-devel necessary to have --enable-gcc-warnings not fail
sudo yum install \
  ocaml-findlib-devel \
  perl-ExtUtils-MakeMaker \
  perl-Test-Pod \
  perl-Test-Pod-Coverage \
  perl-Test-Simple \
  perl-devel \
  perl-libintl \
  readline-devel \
  ruby-devel \
  rubygem-rake
