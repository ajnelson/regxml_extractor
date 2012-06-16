#!/bin/bash

# Copyright (c) 2012, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University of California, Santa Cruz nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    

if [ $# -lt 1 ]; then
  echo "Usage: $0 <disk image>" >&2
  exit 1
fi

#If not installed, just run local scripts
SCRIPT_PREFIX=""
if test "x$(which rx_extract_hives.py)" = "x" ; then
  SCRIPT_PREFIX="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"
fi

#Does it look like we ran before?
if [ $(ls *hive 2>/dev/null | wc -l) -gt 0 ]; then
  echo "Found some hive files.  Assuming extraction has already run.  If this is wrong, remove *.hive"
else
  #Invoke extraction script
  "${SCRIPT_PREFIX}rx_extract_hives.py" --hivexml "$1" >manifest.txt
fi

# For each regxml file generated, run xmllint to validate and pretty-print
rm -f linted.txt out.sqlite
if [ $(ls *hive | wc -l) -eq 0 ]; then
  echo "No hives extracted."
else
  for x in $(ls *hive);
  do
    hivexml "${x}" >"${x}.regxml" 2>${x}.hivexml.err.log && \
    xmllint --format "${x}.regxml" >"${x}.checked.regxml" 2>${x}.xmllint.err.log&& \
    printf "$PWD/$x\t$PWD/$x.regxml\n" >>linted.txt ;
  done
  # When all regxml is pretty-printed, generate a database
  if [ -f linted.txt ]; then
    "${SCRIPT_PREFIX}rx_make_database.py" linted.txt manifest.txt out.sqlite
  fi
fi
