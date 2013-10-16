#!/bin/bash

set -x

"$PYTHON3" regxml_extractor.py -d -Z --path-to-rx-py . analyze_hive ../deps/hivex/images/minimal make_check_results
rc=$?
find junk | sort
exit $rc
