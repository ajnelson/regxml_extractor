#!/bin/bash
RE_HIVEX_CONFIGURE_EXTRA_FLAGS="LDFLAGS=-L/opt/local/lib CPPFLAGS=-I/opt/local/include" \
  INSTALL_DEPS=install_dependent_packages-osx-10.8.sh \
  ./_build_regxml_extractor.sh
