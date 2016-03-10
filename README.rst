tldp - tools for publishing from TLDP sources
=============================================
This package was written for the Linux Documentation Project to help with
management and automation of publication of source documents.  The primary
interface provided is a command-line toolset.

The supported source formats can be listed, but contain at least, Linuxdoc,
DocBookSGML and DocBook XML 4.x.

TLDP = The Linux Documentation Project.

The tools in this package process source documents in the `TLDP document
repository <https://github.com/tLDP/LDP>`_ and generate the following set of
outputs from each source document.

- .pdf, PDF
- .txt, text
- -single.html, a one-page HTML document
- .html, a multipage HTML document

(We may add other output formats.)

Supported input formats are:

- Asciidoc
- Linuxdoc
- Docbook SGML 3.x (though deprecated, please no new submissions)
- Docbook SGML 4.x
- Docbook XML 4.x
- Docbook XML 5.x (basic support, as of 2016-03-10)


Behaviour
---------
There's a source repository which has many source directories containing
documents.  Each directory containing (sourcedir).

A source document can be a file in a sourcedir or a directory in the
sourcedir.  Note that the file Assembly-HOWTO.xml is self-contained.  The
directory BRIDGE-STP-HOWTO a file BRIDGE-STP-HOWTO.sgml.::

  Assembly-HOWTO.xml
  BRIDGE-STP-HOWTO/
  BRIDGE-STP-HOWTO/BRIDGE-STP-HOWTO.sgml
  BRIDGE-STP-HOWTO/images
  BRIDGE-STP-HOWTO/images/hardware-setup.eps
  BRIDGE-STP-HOWTO/images/hardware-setup.png
  BRIDGE-STP-HOWTO/images/old-hardware-setup.eps
  BRIDGE-STP-HOWTO/images/old-hardware-setup.png

Each document can be identified by its stem name.  In the above, the stems are
`Assembly-HOWTO` and `BRIDGE-STP-HOWTO`.

There is a directory containing the output collection.  Each directory is named
by the stem name of the source document and contains the output formats for
each source document.  Here are the corresponding output directories for the
above two documents:::

  Assembly-HOWTO/
  Assembly-HOWTO/Assembly-HOWTO.html
  Assembly-HOWTO/Assembly-HOWTO.pdf
  Assembly-HOWTO/Assembly-HOWTO-single.html
  Assembly-HOWTO/Assembly-HOWTO.txt
  Assembly-HOWTO/index.html
  Assembly-HOWTO/mips.html
  Assembly-HOWTO/nasm.html
    ... and more ...
  
  BRIDGE-STP-HOWTO/
  BRIDGE-STP-HOWTO/BRIDGE-STP-HOWTO.html
  BRIDGE-STP-HOWTO/BRIDGE-STP-HOWTO.pdf
  BRIDGE-STP-HOWTO/BRIDGE-STP-HOWTO-single.html
  BRIDGE-STP-HOWTO/BRIDGE-STP-HOWTO.txt
  BRIDGE-STP-HOWTO/images
  BRIDGE-STP-HOWTO/images/hardware-setup.eps
  BRIDGE-STP-HOWTO/images/hardware-setup.png
  BRIDGE-STP-HOWTO/images/old-hardware-setup.eps
  BRIDGE-STP-HOWTO/images/old-hardware-setup.png
  BRIDGE-STP-HOWTO/index.html
    ... and more ...


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
  By Status Type
  --------------
  source     503  3-Button-Mouse, 3D-Modelling, 4mb-Laptops, and 500 more ...
  output     503  3-Button-Mouse, 3D-Modelling, 4mb-Laptops, and 500 more ...
  published  503  3-Button-Mouse, 3D-Modelling, 4mb-Laptops, and 500 more ...
  stale        0  
  orphan       0  
  broken       1  HOWTO-INDEX
  new          0  

  By Document Type
  ----------------
  Linuxdoc              226  3-Button-Mouse, 3D-Modelling, and 224 more ...
  Docbook4XML           130  8021X-HOWTO, abs-guide, and 128 more ...
  Docbook5XML             1  Assembly-HOWTO
  DocbookSGML           146  ACP-Modem, and 145 more ...

To build and publish a single document:::

  $ ldptool --publish DocBook-Demystification-HOWTO
  $ ldptool --publish ~/vcs/LDP/LDP/howto/docbook/Valgrind-HOWTO.xml

To build and publish anything that is new or updated work:::

  $ ldptool --publish
  $ ldptool --publish work

To (re-)build and publish everything, regardless of state:::

  $ ldptool --publish all

To generate a specific output (into a --builddir):::

  $ ldptool --build DocBook-Demystification-HOWTO

To generate all outputs into a --builddir (should exist):::

  $ ldptool --builddir ~/tmp/scratch-directory/ --build all

To build new/updated work, but pass over a trouble-maker:::

  $ ldptool --build --skip HOWTO-INDEX

To loudly generate all outputs, except a trouble-maker:::

  $ ldptool --build all --loglevel debug --skip HOWTO-INDEX

To print out a shell script for building a specific document:::

  $ ldptool --script TransparentProxy
  $ ldptool --script ~/vcs/LDP/LDP/howto/docbook/Assembly-HOWTO.xml


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
- linuxdoc-tools{,-text,-latex}
- docbook{,-dsssl,-xsl,-utils}
- htmldoc{,-common}
- xsltproc
- fop
- sgml2x
- opensp
- openjade
- ldp-docbook-xsl
- ldp-docbook-dsssl
- html2text
- docbook5-xml
- docbook-xsl-ns
- jing
- asciidoc
- libxml2-utils

OpenSUSE
++++++++
- htmldoc
- openjade
- sgmltool
- html2text
- docbook{,5}-xsl-stylesheets
- docbook-dsssl-stylesheets
- docbook-utils-minimal
- docbook-utils
- jing
- asciidoc
- libxml2-tools
- libxslt-tools

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

* `Source tree on GitHub <https://github.com/tLDP/LDP>`_
* `Output documentation tree (sample) <http://www.tldp.org/>`_


