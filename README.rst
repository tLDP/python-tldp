tldp - tools for publishing from TLDP sources
=============================================

.. image:: https://api.travis-ci.org/martin-a-brown/python-tldp.svg
    :target: https://github.com/tLDP/python-tldp

.. image:: http://img.shields.io/badge/license-MIT-brightgreen.svg 
    :target: http://opensource.org/licenses/MIT
    :alt: MIT license

This package was written for the Linux Documentation Project (TLDP) to help
with management and publication automation of source documents.  The primary
interface provided is a command-line tool caalled `ldptool`.  The canonical
location of this software is:

  https://github.com/tLDP/python-tldp/

The `ldptool` executable can:

- crawl through any number of source collection directories
- crawl through a single output collection
- match the sources to the outputs (based on document stem name)
- describe supported source formats (`--formats`)
- describe the meaning of document status (`--statustypes`)
- describe the collection by type and status (`--summary`)
- list out individual document type and status (`--list`)
- build the expected (non-configurable) set of outputs (`--build`)
- build and publish the outputs (`--publish`)
- produce runnable shell script to STDOUT (`--script`)

The tools in this package process source documents in the `TLDP document
repository <https://github.com/tLDP/LDP>`_ and generate the following set of
outputs from each source document.

- .pdf, PDF
- .txt, text
- -single.html, a one-page HTML document
- .html, a multipage HTML document

(We may add other output formats; an epub format is under consideration.)

Supported input formats are:

- Asciidoc
- Linuxdoc
- Docbook SGML 3.x (though deprecated, please no new submissions)
- Docbook SGML 4.x
- Docbook XML 4.x
- Docbook XML 5.x (basic support, as of 2016-03-10)


Example usages
--------------
If your attempts to run the below commands don't work or generate errors, see
also `Minimal configuration`_.

Here are some example usages against a live checkout of the LDP source
repository and a local cache of the output tree:

To see what work needs to be done, `ldptool --list`::

  $ ldptool  --list
  orphan    <unknown>            Bugzilla-Guide
  new       DocBook XML 4.x      DocBook-Demystification-HOWTO
  stale     DocBook XML 4.x      Linux-Dictionary
  broken    DocBook SGML 3.x/4.x PHP-Nuke-HOWTO
  stale     Linuxdoc             User-Group-HOWTO

To see publication status of each document:::

  $ ldptool --list all | head -n 3
  published Linuxdoc             3-Button-Mouse                                 
  published Linuxdoc             3D-Modelling                                   
  published Linuxdoc             4mb-Laptops                                    

To get more information about the newer or missing files in a specific
document:::

  $ ldptool --verbose --list Linux-Dictionary
  stale     DocBook XML 4.x      Linux-Dictionary
           doctype <class 'tldp.doctypes.docbook4xml.Docbook4XML'>
        output dir /home/mabrown/tmp/en/Linux-Dictionary
       source file /home/mabrown/vcs/LDP/LDP/guide/docbook/Linux-Dictionary/Linux-Dictionary.xml
      newer source /home/mabrown/vcs/LDP/LDP/guide/docbook/Linux-Dictionary/Contributors.xml
      newer source /home/mabrown/vcs/LDP/LDP/guide/docbook/Linux-Dictionary/D.xml
      newer source /home/mabrown/vcs/LDP/LDP/guide/docbook/Linux-Dictionary/J.xml
      newer source /home/mabrown/vcs/LDP/LDP/guide/docbook/Linux-Dictionary/O.xml
      newer source /home/mabrown/vcs/LDP/LDP/guide/docbook/Linux-Dictionary/S.xml

To see what the entire source collection looks like, use `ldptool --summary`:::

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


Logging
-------
The `ldptool` utility is largely written to be interactive or a supervised
batch process.  It uses STDERR as its logstream and sets the default loglevel
at logging.ERROR.  At this log level, in `--script`, `--build` and `--publish`
mode, it should report nothing to STDERR.  To increase progress verbosity,
setting the loglevel to info (`--loglevel info`) may help with understanding
what work the tool is performing.  If you need to collect diagnostic
information for troubleshooting or bug reports, `ldptool` supports `--loglevel
debug`.


Configuration
-------------
The `ldptool` comes with support for reading its settings from the
command-line, environment or a system and/or user-specified configuration
file.  If you want to generate a sample configuration file to edit and use
later, you can run:::

  ldptool --dump-cfg > my-ldptool.cfg
  ldptool --configfile my-ldptool.cfg --list
  LDPTOOL_CONFIGFILE=/path/to/ldptool.cfg ldptool --list


Source document identification
------------------------------
TLDP's source repository contains many separate directories containing
documents (e.g. LDP/howto/docbook, LDP/howto/linuxdoc).  Each of these
directories may contain documents; to `ldptool` each of these is a
`--sourcedir`.

A source document (in a `--sourcedir`) can be a file or a directory.  Here are
two examples.  The Assembly-HOWTO.xml is an entire document stored as a single
file.  The directory BRIDGE-STP-HOWTO exists and contains its main document, a
file named BRIDGE-STP-HOWTO.sgml.  In the case of a source document that is a
directory, the stem name of the primary document must match the name of the
directory.::

  Assembly-HOWTO.xml
  BRIDGE-STP-HOWTO/
  BRIDGE-STP-HOWTO/BRIDGE-STP-HOWTO.sgml
  BRIDGE-STP-HOWTO/images
  BRIDGE-STP-HOWTO/images/hardware-setup.eps
  BRIDGE-STP-HOWTO/images/hardware-setup.png
  BRIDGE-STP-HOWTO/images/old-hardware-setup.eps
  BRIDGE-STP-HOWTO/images/old-hardware-setup.png

Each document for a single run of `ldptool` can be uniquely identified by its
stem name.  In the above, the stems are `Assembly-HOWTO` and
`BRIDGE-STP-HOWTO`.  It is an error to have two documents with the same stem
name and the second discovered document will be ignored.

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


Minimal configuration
---------------------
The most important configuration parameters that `ldptool` takes are the set
of source directories (in which to find documents) and the output directory,
in which to create the resulting outputs.  It will not be able to run unless
it has at least one --sourcedir and an existing --pubdir directory.

If you have an LDP checkout in your home directory, here's an example which
would process all of the Linuxdoc HOWTO docs:::

  mkdir LDP-output-tree
  ldptool --sourcedir $HOME/LDP/LDP/howto/linuxdoc --pubdir LDP-output-tree

If you would like to create a sample configuration file for use later (or for
copying into the system location, `/etc/ldptool/ldptool.ini`, you can generate
your own config file as follows:::

  ldptool > sample-ldptool.cfg \
          --sourcedir $HOME/LDP/LDP/faq/linuxdoc/ \
          --sourcedir $HOME/LDP/LDP/guide/linuxdoc/ \
          --sourcedir $HOME/LDP/LDP/howto/linuxdoc/ \
          --sourcedir $HOME/LDP/LDP/howto/docbook/ \
          --sourcedir $HOME/LDP/LDP/guide/docbook/ \
          --sourcedir $HOME/LDP/LDP/ref/docbook/ \
          --sourcedir $HOME/LDP/LDP/faq/docbook/ \
          --pubdir $HOME/LDP-output/ \
          --loglevel info \
          --dump-cfg

Then, you can run the same configuration again with:::

  ldptool --configfile sample-ldptool.cfg

The `ldptool` program tries to locate all of the tools it needs to process
documents.  Each source format requires a certain set of tools, for example, to
process DocBook 4.x XML, `ldptool` needs the executables xmllint, xstlproc,
html2text, fop and dblatex.  It also requires the XSL files for generating FO,
chunked HTML and single-page HTML.  All of the items are configurable on the
command-line or in the configuration file, but here's a sample config file
stanza:::

  [ldptool-docbook4xml]
  xslchunk = /usr/share/xml/docbook/stylesheet/ldp/html/tldp-sections.xsl
  xslsingle = /usr/share/xml/docbook/stylesheet/ldp/html/tldp-one-page.xsl
  fop = /usr/bin/fop
  dblatex = /usr/bin/dblatex
  xsltproc = /usr/bin/xsltproc
  html2text = /usr/bin/html2text
  xslprint = /usr/share/xml/docbook/stylesheet/ldp/fo/tldp-print.xsl
  xmllint = /usr/bin/xmllint

The above stanza was generated by running `ldptool --dump-cfg` on an Ubuntu
14.04 system which had all of the software dependencies installed.  If your
distribution does not supply ldp-docbook-xsl, for example, you would need to
fetch those files, put them someplace in the filesystem and adjust your
configuration file or command-line invocations accordingly.


Software dependencies
---------------------
There are a large number of packages listed here in the dependency set.  This
is because the supporting software for processing Linuxdoc and the various
DocBook formats is split across many upstream packages and repositories.

The generated python packages (see below) do not include the explicit
dependencies to allow the package manager (e.g. apt, zypper, dnf) to install
the dependencies.  This would be a nice improvement.

Here are the dependencies needed for this tool to run:

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


Supported Python versions
-------------------------
This package was developed against Python-2.7.8 and Python-3.4.1 (on
OpenSUSE).  It has been used on Python-2.7.6 (Ubuntu-14.04) and Python-3.4.2 and Python-2.7.9 (on Debian 8).

Continuous Integration testing information and coverage can be reviewed at
`this project's Travis CI page <https://travis-ci.org/martin-a-brown/python-tldp/>`_.


Installation
------------
This is a pure-Python package, and you should be able to use your favorite
Python tool to install it on your system.  The python-tldp package (`ldptool`)
requires a large number of other packages, most of which are outside of the
Python ecosystem.  There's room for improvement here, but here are a few
tidbits.

Build an RPM::

  python setup.py sdist && rpmbuild -ta ./dist/python-tldp-${VERSION}.tar.gz

There's a generated file, `contrib/tldp.spec`, which makes a few changes to the
setuptools stock-generated specfile.  It adds the dependencies, marks the
configuration file as %config(noreplace), adds a manpage and names the binary
package `python-tldp`.

Build a DEB::

Check to see if the package is available from upstream.  It may be included in
the Debian repositories already::

  apt-cache search tldp

The quick and dirty way is as follows::

  python setup.py --command-packages=stdeb.command bdist_deb

But, there is also a `debian` directory.  If you are working straight from the
git checkout, you should be able to generate an installable (unsigned) Debian
package with::

  bash contrib/debian-release.sh -us -uc

Install using pip:

Unknown.  Because the tool relies so heavily on system-installed non-Python
tools, I have not bothered to try installing the package using pip.  It should
work equivalently as well as running the program straight from a checkout.
If you learn anything here or have suggestions, for me, please feel free to
send them along.


Links
-----

* `Canonical python-tldp repository <https://github.com/tLDP/python-tldp>`_
* `Source tree on GitHub <https://github.com/tLDP/LDP>`_
* `Output documentation tree (sample) <http://www.tldp.org/>`_
