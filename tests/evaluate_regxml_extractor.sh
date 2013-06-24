#!/bin/bash

usage="Usage: $0 [options] disk_image_list_txt\n"
usage=$usage"\n"
usage=$usage"Options:\n"
usage=$usage"\t-d, --debug\n"
usage=$usage"\t  Enable debug output (writes to stderr).\n"
usage=$usage"\t--force-fiwalk\n"
usage=$usage"\t  Force fiwalk to run.\n"
usage=$usage"\t-j\n"
usage=$usage"\t  Execute RegXML Extractor on disk images in parallel.  Requires GNU Parallel.\n"
usage=$usage"\n"

usage_exit() {
  printf "$usage" >&2
  exit 1
}

GPARALLEL=$(which parallel)

debug=0
do_parallel=0
force_fiwalk=

while [ $# -ge 1 ]; do
  case $1 in
    -d | --debug )
      debug=1
      ;;
    --force-fiwalk )
      force_fiwalk=--force-fiwalk
      ;;
    -j )
      do_parallel=1
      if [ -z "$GPARALLEL" ]; then
        echo "Warning: Could not find GNU Parallel in \$PATH.  Will execute in serial." >&2
        do_parallel=0
      fi
      ;;
    * )
      break
      ;;
  esac
  shift
done

if [ $# -ne 1 ]; then
  usage_exit
fi

imglist=$1

if [ ! -r "$imglist" ]; then
  echo "Image list ($imglist) is not a readable file." >&2
  exit 1
fi

#One-liner c/o http://stackoverflow.com/a/246128/1207160
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#Change to the script's directory so we can get Git metadata
pushd "$script_dir" >/dev/null

outdir_root=evaluations_by_commit/$(git rev-parse HEAD)

mkdir -p "$outdir_root"

if [ $do_parallel -ne 1 ]; then
  echo "Note: Executing RE in serial." >&2
  while read x; do
    if [ -r "$x.dfxml" ]; then
      if [ $debug -eq 1 ]; then
        echo "Debug: Processing $x..." >&2
      fi
      ./log_re_on_one_image.sh "$x" "$outdir_root"
    fi
  done <"$imglist"
else
  echo "Note: Executing RE in parallel." >&2
  report_progress=
  if [ $debug -eq 1 ]; then
    report_progress=--progress
  fi
  #AJN TODO Ubuntu 12.10 was triggering the '--tollef' flag somehow; that will be retired 20140222. At that point, '--gnu' can be dropped from this command.
  parallel --gnu $report_progress --keep-order ./log_re_on_one_image.sh $force_fiwalk {} "$outdir_root" :::: "$imglist"
fi

echo "Number of disk images processing successes: $(grep '0' ${outdir_root}/*.status.log | wc -l)"
echo "Number of disk images processing errors: $(grep -v '0' ${outdir_root}/*.status.log | wc -l)"

popd >/dev/null
