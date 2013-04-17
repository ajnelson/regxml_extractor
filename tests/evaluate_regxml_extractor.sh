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

#TODO pushd into here.

mkdir evaluation
while read x; do
  if [ -r "$x.dfxml" ]; then
    bn=$(basename $x)
    mkdir -p "evaluations_by_commit/$githead/$bn"
    pushd "evaluations_by_commit/$githead/$bn"
    regxml_extractor.sh -x "$x.dfxml" "$x" >"../$bn.out.log" 2>"../$bn.err.log"
    echo $? >../$bn.status.log
    popd
  fi
done <"$imglist"
