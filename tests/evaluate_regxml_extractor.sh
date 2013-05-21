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

githead=$(git rev-parse HEAD)

mkdir -p evaluation
while read x; do
  if [ -r "$x.dfxml" ]; then
    bn=$(basename "$x")
    outdir=evaluations_by_commit/$githead/$bn
    regxml_extractor.sh -d -o "$outdir" -x "$x.dfxml" "$x" >"${outdir}.out.log" 2>"${outdir}.err.log"
    echo $? >${outdir}.status.log
  fi
done <"$imglist"

echo "Number of disk images processing errors: $(grep -v '0' evaluation/$githead/*.status.log | wc -l)"
