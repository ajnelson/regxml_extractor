regxmlify
=========

Converts Windows Registry hives to a descriptive XML format.

The collective software in this project takes a disk image and outputs a set of RegXML files, one per hive extracted from the image.

Dependencies
============

This program depends on Fiwalk and Hivex.

To install hivex, you must have the following packages installed (assuming a default environment for the named distros):

Fedora 16: gcc libxml2-devel python-devel

Ubuntu 12.04: libxml2-dev python-dev

A version of Hivex that generates RegXML can be found [here](https://github.com/ajnelson/hivex/tree/nelson_ifip12).

To install Fiwalk, compile the Sleuth Kit provided [here](https://github.com/kfairbanks/sleuthkit).

This Fiwalk, embedded in The Sleuth Kit, has a dependency on Java, which can be satisfied with the Oracle Java Development Kit (JDK) RPM.

Your environment's PYTHONPATH variable must include the Fiwalk python directory, which would be under:
<sleuthkit directory>/tools/fiwalk/python

References
==========

RegXML is described in the following publication, in which it was used as an analysis tool:

Alex Nelson, "RegXML: XML conversion of the Windows Registry for forensic processing and distribution," in _Advances in Digital Forensics VIII, to appear Summer 2012_, ser. IFIP Advances in Information and Communication Technology, G. Peterson and S. Shenoi, Eds. Springer, 2012.

The software here was formerly housed at:

https://users.soe.ucsc.edu/~ajnelson/research/nelson_ifip12/
