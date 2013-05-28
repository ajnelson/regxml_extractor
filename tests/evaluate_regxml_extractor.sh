#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 disk_image_list_txt" >&2
  exit 1
fi

imglist=$1

if [ ! -r "$imglist" ]; then
  echo "Image list ($imglist) is not a readable file." >&2
  exit 1
fi

#TODO Change pwd to here, to be in Git source directory
outdir_root=evaluations_by_commit/$(git rev-parse HEAD)

mkdir -p "$outdir_root"
while read x; do
  if [ -r "$x.dfxml" ]; then
    outdir=${outdir_root}/$(basename "$x")
    regxml_extractor.sh -d -o "$outdir" -x "$x.dfxml" "$x" >"${outdir}.out.log" 2>"${outdir}.err.log"
    echo $? >${outdir}.status.log
  fi
done <"$imglist"

echo "Number of disk images processing errors: $(grep -v '0' ${outdir_root}/*.status.log | wc -l)"
