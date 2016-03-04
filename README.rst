tldp - tools for publishing from TLDP sources
=============================================
A toolset for publishing multiple output formats of a source document to an
output directory.  The supported source formats can be listed, but contain at
least, Linuxdoc, DocBookSGML and DocBook XML 4.x.

TLDP = The Linux Documentation Project.

These are a set of scripts that process committed documents in the
TLDP document source repository to an output tree of choice.


Example usages:
---------------

Here are some example usages against a live checkout of the LDP source
repository and a local cache of the output tree:

To see what work needs to be done, `ldptool --list`::

  $ ldptool  --list
  new       DocBook-Demystification-HOWTO                  
  stale     Linux-Dictionary                               
  broken    PHP-Nuke-HOWTO                                 
  orphan    Traffic-Control-tcng-HTB-HOWTO   

To see publication status of each document:::

  $ ldptool --list all | head -n 3
  published 3-Button-Mouse                                 
  published 3D-Modelling                                   
  published 4mb-Laptops  

To get more information about the newer or missing files in a specific
document:::

  $ ldptool --list Linux-Dictionary
  stale     Linux-Dictionary
      newer source /vcs/LDP/LDP/guide/docbook/Linux-Dictionary/Contributors.xml
      newer source /vcs/LDP/LDP/guide/docbook/Linux-Dictionary/D.xml
      newer source /vcs/LDP/LDP/guide/docbook/Linux-Dictionary/J.xml
      newer source /vcs/LDP/LDP/guide/docbook/Linux-Dictionary/O.xml
      newer source /vcs/LDP/LDP/guide/docbook/Linux-Dictionary/S.xml

To get the big picture:::

  $ ldptool --summary
  source     503  3-Button-Mouse, 3D-Modelling, 4mb-Laptops, and 500 more ...
  output     503  3-Button-Mouse, 3D-Modelling, 4mb-Laptops, and 500 more ...
  published  503  3-Button-Mouse, 3D-Modelling, 4mb-Laptops, and 500 more ...
  new          1  DocBook-Demystification-HOWTO
  orphan       1  Traffic-Control-tcng-HTB-HOWTO
  broken       1  HOWTO-INDEX
  stale        1  Linux-Dictionary

To generate a specific output:::

  $ ldptool --build DocBook-Demystification-HOWTO

To generate all outputs:::

  $ ldptool --build

To generate all outputs, except a trouble-maker:::

  $ ldptool --build --skip HOWTO-INDEX

To loudly generate all outputs, except a trouble-maker:::

  $ ldptool --build --loglevel debug --skip HOWTO-INDEX

To print out a script of what would be executed:::

  $ ldptool --script DocBook-Demystification-HOWTO


Configuration
-------------
The `ldptool` comes with support for reading its settings from the
command-line, environment or a system and/or user-specified configuration
file.  If you want to generate a sample configuration file to edit and use
later, you can run:::

  ldptool --dump-cfg > my-ldptool.cfg
  ldptool --configfile my-ldptool.cfg --list
  LDPTOOL_CONFIGFILE=/path/to/ldptool.cfg ldptool --list


Software dependencies
---------------------
There are a large number of packages listed here in the dependency set.  This
is because the supporting software for processing Linuxdoc and the various
DocBook formats is split across many upstream packages and repositories.

Ubuntu / Debian
+++++++++++++++
- git{,-core,-doc,-man}
- linuxdoc-tools{,-text,-latex}
- docbook{,-dsssl,-xsl,-utils}
- htmldoc{,-common}
- xsltproc
- libxml2-utils
- fop
- sgml2x
- openjade
- opensp
- ldp-docbook-xsl
- ldp-docbook-dsssl
- html2text
- docbook5-xml
- docbook-xsl-ns
- jing

OpenSUSE
++++++++
- htmldoc
- openjade
- sgmltool
- html2text
- libxml2-tools
- libxslt-tools
- docbook{,5}-xsl-stylesheets
- docbook-dsssl-stylesheets
- docbook-utils-minimal
- jing

There are a few additional data files that are needed, specifically, the TLDP
XSL and DSSSL files that are used by the respective DocBook SGML (openjade) and
DocBook XML (xsltproc) processing engines to generate the various outputs.

On Debian-based systems, there are packages available from the distributor
called ldp-docbook-{xsl,dsssl}.  There aren't any such packages for RPM (yet).


Installation
------------
This is a pure-Python package, and you should be able to use your favorite
Python tool to install it on your system.  The python-tldp package (`ldptool`)
requires a large number of other packages, most of which are outside of the
Python ecosystem.  There's room for improvement here, but here are a few
tidbits.

Build an RPM:::

  python setup.py bdist_rpm

There's a file, `contrib/tldp.spec`, which makes a few changes to the
setuptools stock-generated specfile.  Specifically, the package gets named
`python-tldp` instead of `tldp` and the configuration file is marked
`%config(noreplace)`.

I know less about packaging for Debian.  Relying on python-stdeb yields a
working and usable Debian package which has been tested out on an Ubuntu
14.04.3 system.

Build a DEB:::

  python setup.py --command-packages=stdeb.command bdist_deb

I have not tried installing the package in a virtualenv or with pip.  If you
try that, please let me know any problems you encounter.


Links
-----

* `Output documentation tree (sample) <http://www.tldp.org/>`_

* `Source tree on GitHub <https://github.com/tLDP/LDP>`_

