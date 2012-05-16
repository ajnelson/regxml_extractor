#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <disk image>" >&2
  exit 1
fi

#If not installed, just run local scripts
SCRIPT_PREFIX=""
if test "x$(which extract_hives.py)" = "x" ; then
  SCRIPT_PREFIX="./"
fi

#Does it look like we ran before?
if [ $(ls *hive | wc -l) -gt 0 ]; then
  echo "Found some hive files.  Assuming extraction has already run.  If this is wrong, remove *.hive"
else
  #Invoke extraction script
  "${SCRIPT_PREFIX}extract_hives.py" --hivexml "$1" >manifest.txt
fi

# For each regxml file generated, run xmllint to validate and pretty-print
rm -f linted.txt
if [ $(ls *hive | wc -l) -eq 0 ]; then
  echo "No hives extracted."
else
  for x in $(ls *hive);
  do
    hivexml "${x}" >"${x}.regxml" 2>${x}.hivexml.err.log && \
    xmllint --format "${x}.regxml" >"${x}.checked.regxml" 2>${x}.xmllint.err.log&& \
    echo $x >>linted.txt ;
  done
  # When all regxml is pretty-printed, generate a database
  if [ -f linted.txt ]; then
    "${SCRIPT_PREFIX}make_database.py" linted.txt manifest.txt out.sqlite
  fi
fi
