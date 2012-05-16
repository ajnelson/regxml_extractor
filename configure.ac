#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.61)
AC_INIT(regxmlify, 0.1.0, ajnelson@cs.ucsc.edu)
AM_INIT_AUTOMAKE(regxmlify, 0.1.0)
AC_OUTPUT(Makefile scripts/Makefile)

# Checks for programs.

AC_CHECK_PROG(HAVE_FIWALK,fiwalk,yes)
if test "$HAVE_FIWALK" != "yes"; then
  AC_MSG_ERROR([fiwalk not found; refer to README for compilation notes.])
fi

AC_CHECK_PROG(HAVE_HIVEXML,hivexml,yes)
if test "$HAVE_HIVEXML" != "yes"; then
  AC_MSG_ERROR([hivexml not found; refer to README for compilation notes.])
fi

AC_CHECK_PROG(HAVE_XMLLINT,xmllint,yes)
if test "$HAVE_XMLLINT" != "yes"; then
  AC_MSG_ERROR([xmllint not found; the package for libxml2 includes this.])
fi

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

#AJN Not sure I want these yet...
#AC_CONFIG_SUBDIRS([deps/fiwalk
#                   deps/hivex])

AC_OUTPUT
