#!/bin/bash

echo "Note: Debian 7.0.0's ~/.bashrc includes an interactive-shell-only directive.  Hence, RegXML Extractor's bashrc modifications are imported into this test script's execution environment directly, and you will need to update your shell's environment (or start a new shell) to inherit the ~/local path updates." >&2
source ../../deps/bashrc

INSTALL_DEPS=install_dependent_packages-debian-7.0.0.sh ./_build_regxml_extractor.sh
