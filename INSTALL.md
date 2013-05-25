# Installing RegXML Extractor

This document details how to build RegXML Extractor ("RE" in this file) and its dependent software.


## Easy Build

The most straightforward compilation is to run a script used to test RE's build: `tests/for_throwaway_vms_only` contains shell scripts that *locally* build, check, and install RE and component programs.  Run the `build_on_` script appropriate for your operating system version.  You will need sudo privileges to install some packages from your distribution's package manager, but everything else is built locally.

One caveat with this one-script installation approach is that the local build process updates your shell's initialization commands to allow for local compilations and linking (under prefix `~/local`); see `deps/bashrc` for the augmentations performed.

The deciding questions on whether or not to use the easy build are:
* Do I want to install RegXML Extractor system-wide? (no -> use easy build)
* Do I want to compile and install other software *without* potentially clobbering package-managed software? (yes -> use easy build)
* Do I have administrator permission and need to globally install non-package-managed software? (no -> use easy build)


## Installing RegXML Extractor system-wide

Currently, the Easy Build above is recommended over installing system-wide.

Building from Git is recommended over building from a tarball.  This is because currently there is some dependent software that is not in distros' package managers (specifically, the recent Sleuth Kit and RE's modified Hivex).


### From Git

First, ensure you have the packages you'll need:

    sudo deps/install_dependent_packages-(os)-(version).sh

Then ensure the tracked software is built and installed (you'll need `sudo`):

    deps/build_submodules.sh system

Last, `configure...` builds RE:

    ./configure && make && sudo make install


## Testing

RE tracks testing and evaluation of its "master" and "unstable" branches in Git.  "Testing" is running the script `tests/for_throwaway_vms_only/build_on_(os-version).sh` in a clean, snapshotted virtual machine.  "Evaluating" is running RegXML Extractor against a corpus of disk images noted on [Digital Corpora](http://www.forensicswiki.org/wiki/Forensic_corpora), without RE exiting in an error state on any of the images.

To see how tested your distro is, get the testing branch name from this list:

    git branch -r | egrep 'tested|evaluated'

And run `gitk` with the desired branch and test.  E.g. to see how checked RE is doing in development for CentOS, this command shows the logs:

    gitk \
      origin/evaluated/unstable/centos-6.4 \
      origin/tested/unstable/centos-6.4 \
      unstable

If you try the testing process yourself and encounter an error, please describe the OS and test script you used in a [Github Issue](https://github.com/ajnelson/regxml_extractor/issues).