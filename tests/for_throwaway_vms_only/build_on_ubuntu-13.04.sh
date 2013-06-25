#!/bin/bash

echo "Note: Ubuntu 13.04's ~/.bashrc includes an interactive-shell-only directive.  Hence, RegXML Extractor's bashrc modifications are imported into this test script's execution environment directly, and you will need to update your shell's environment (or start a new shell) to inherit the ~/local path updates." >&2
source ../../deps/bashrc
cat ../../deps/bashrc >>~/.bashrc

INSTALL_DEPS=install_dependent_packages-ubuntu-13.04.sh ./_build_regxml_extractor.sh
