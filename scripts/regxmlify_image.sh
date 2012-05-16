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

# Invoke extraction script
"${SCRIPT_PREFIX}extract_hives.py" --hivexml "$1" >manifest.txt
# For each regxml file generated, run xmllint to validate and pretty-print
rm -f linted.txt
if [ $(ls *hive | wc -l) -eq 0 ]; then
  echo "No hives extracted."
else
  for x in $(ls *hive); do xmllint --format "$x" >"${x}.checked.regxml" && echo $x >>linted.txt ; done
  # When all regxml is pretty-printed, generate a database
  if [ -f linted.txt ]; then
    "${SCRIPT_PREFIX}make_database.py" linted.txt manifest.txt out.sqlite
  fi
fi
