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

#One-liner c/o http://stackoverflow.com/a/246128/1207160
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "$script_dir" >/dev/null

outdir_root=evaluations_by_commit/$(git rev-parse HEAD)

mkdir -p "$outdir_root"

GPARALLEL=$(which parallel)
if [ -z "$GPARALLEL" ]; then
  echo "Note: Executing RE in serial." >&2
  while read x; do
    if [ -r "$x.dfxml" ]; then
      ./log_re_on_one_image.sh "$x" "$outdir_root"
    fi
  done <"$imglist"
else
  echo "Note: Executing RE in parallel." >&2
  parallel --progress --keep-order ./log_re_on_one_image.sh {} "$outdir_root" :::: "$imglist"
fi

echo "Number of disk images processing successes: $(grep '0' ${outdir_root}/*.status.log | wc -l)"
echo "Number of disk images processing errors: $(grep -v '0' ${outdir_root}/*.status.log | wc -l)"

popd >/dev/null
