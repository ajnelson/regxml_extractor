#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.61)
AC_INIT(regxml_extractor, 0.3.0, ajnelson@cs.ucsc.edu)
AM_INIT_AUTOMAKE(regxml_extractor, 0.3.0)
AC_OUTPUT(Makefile lib/Makefile scripts/Makefile)

# Checks for programs.

if test "$(uname -s)" = "Darwin"; then
  AC_CHECK_PROG(HAVE_GETOPT,getopt,yes,,/opt/local/bin/getopt)
  if test "$HAVE_GETOPT" = "yes"; then
    AC_SUBST(GNU_GETOPT,/opt/local/bin/getopt)
  else
    AC_MSG_ERROR([OS X environment detected, but GNU getopt not found; please install the MacPort package 'getopt'.  The BSD getopt included with OS X is known to be problematic.])
  fi
else
  AC_CHECK_PROG(HAVE_GETOPT,getopt,yes)
  if test "$HAVE_GETOPT" = "yes"; then
    AC_SUBST(GNU_GETOPT,getopt)
  else
    AC_MSG_ERROR([GNU getopt not found.])
  fi
fi

AC_CHECK_PROG(HAVE_HIVEXML,hivexml,yes)
if test "$HAVE_HIVEXML" != "yes"; then
  AC_MSG_ERROR([hivexml not found; refer to the README for Hivex compilation notes.])
fi

AC_CHECK_PROG(HAVE_ICAT,icat,yes)
if test "$HAVE_ICAT" != "yes"; then
  AC_MSG_ERROR([icat not found; refer to the README for Sleuth Kit compilation notes.])
fi

AC_CHECK_PROG(HAVE_FIWALK,fiwalk,yes)
if test "$HAVE_FIWALK" != "yes"; then
  AC_MSG_ERROR([fiwalk not found; refer to the README for Sleuth Kit compilation notes.])
fi

AC_CHECK_PROG(HAVE_XMLLINT,xmllint,yes)
if test "$HAVE_XMLLINT" != "yes"; then
  AC_MSG_ERROR([xmllint not found; refer to the README notes on xmllint.])
fi

AM_PATH_PYTHON(2.7)

AX_PYTHON_MODULE(argparse)
if test "$HAVE_PYMOD_ARGPARSE" != "yes"; then
  AC_MSG_ERROR([Argparse Python module not found; this can be installed with 'easy_install argparse'.])
fi

AX_PYTHON_MODULE(dfxml)
if test "$HAVE_PYMOD_DFXML" != "yes"; then
  AC_MSG_ERROR([DFXML Python module not found; refer to the README notes on PYTHONPATH.])
fi

AX_PYTHON_MODULE(fiwalk)
if test "$HAVE_PYMOD_FIWALK" != "yes"; then
  AC_MSG_ERROR([Fiwalk Python module not found; refer to the README notes on PYTHONPATH.])
fi

AC_CONFIG_FILES([
  scripts/regxml_extractor.sh
])

AC_OUTPUT
