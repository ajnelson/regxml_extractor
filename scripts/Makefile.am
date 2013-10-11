#repdir: RegXML Extractor Python directory
repdir = ${pkgdatadir}/python

rep_DATA = \
  _autotool_vars.py \
  dfxml_tool.py

rep_PYTHON = \
  flatten_regxml.py \
  rdifference.py \
  regxml_extractor.py \
  rx_extract_hives.py \
  rx_make_database.py \
  rx_make_flat_regxml.py

bin_SCRIPTS = regxml_extractor.sh

EXTRA_DIST = \
  _autotool_vars_py_from_sh.sh.in \
  dfxml_tool.py \
  flatten_regxml.py \
  rdifference.py \
  regxml_extractor.py \
  regxml_extractor.sh \
  rx_extract_hives.py \
  rx_make_database.py \
  rx_make_flat_regxml.py

_autotool_vars.py: _autotool_vars_py_from_sh.sh
	bash $< >$@
