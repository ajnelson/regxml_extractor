#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: $0 disk_image output_root" >&2
  echo "" >&2
  echo "Creates RegXML Extractor output in <output_root>/<basename of disk_image>"
  exit 1
fi

img_abs_path=$(python -c 'import sys, os; print(os.path.realpath(sys.argv[1]))' "$1")
output_dir=$2/$(basename "$1")

regxml_extractor.sh -d -o "$output_dir" -x "${img_abs_path}.dfxml" "$img_abs_path" >"${output_dir}.out.log" 2>"${output_dir}.err.log"
echo $? >"${output_dir}.status.log"
