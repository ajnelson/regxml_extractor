#!/bin/bash

set -e

echo "Note: There is a package dependency error between 'audit' and 'glibc'; installing 'audit' first works around this issue."
set -x
sudo yum --assumeyes install audit


INSTALL_DEPS=install_dependent_packages-fedora-18.sh ./_build_regxml_extractor.sh
