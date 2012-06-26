#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.61)
AC_INIT(regxml_extractor, 0.2.0, ajnelson@cs.ucsc.edu)
AM_INIT_AUTOMAKE(regxml_extractor, 0.2.0)
AC_OUTPUT(Makefile scripts/Makefile)

# Checks for programs.

AC_CHECK_PROG(HAVE_ICAT,icat,yes)
if test "$HAVE_ICAT" != "yes"; then
  AC_MSG_ERROR([icat not found; refer to README for SleuthKit compilation notes.])
fi

AC_CHECK_PROG(HAVE_FIWALK,fiwalk,yes)
if test "$HAVE_FIWALK" != "yes"; then
  AC_MSG_ERROR([fiwalk not found; refer to README for SleuthKit compilation notes.])
fi

AC_CHECK_PROG(HAVE_HIVEXML,hivexml,yes)
if test "$HAVE_HIVEXML" != "yes"; then
  AC_MSG_ERROR([hivexml not found; refer to README for Hivex compilation notes.])
fi

AC_CHECK_PROG(HAVE_XMLLINT,xmllint,yes)
if test "$HAVE_XMLLINT" != "yes"; then
  AC_MSG_ERROR([xmllint not found; this may be in libxml2 or the associated utilities package.  Install the package with 'apt-get install libxml2-utils' or 'yum install TODO'.])
fi

AM_PATH_PYTHON(2.7)

AX_PYTHON_MODULE(dfxml)
if test "$HAVE_PYMOD_DFXML" != "yes"; then
  AC_MSG_ERROR([DFXML Python module not found; refer to the README's notes on PYTHONPATH.])
fi

AX_PYTHON_MODULE(fiwalk)
if test "$HAVE_PYMOD_FIWALK" != "yes"; then
  AC_MSG_ERROR([Fiwalk Python module not found; refer to the README's notes on PYTHONPATH.])
fi

AC_OUTPUT
