:orphan:

ldptool manual page
===================

Synopsis
--------

**ldptool** [*options*]  [*pathname* [...]]


Description
-----------

:program:`ldptool` creates chunked HTML, single-page HTML, PDF and plain text
outputs for each source document it is passed as a *pathname*.  See
`Source document discovery`_.

If it is not passed any arguments, `ldptool` will collect all of the
directories specified with the --sourcedir option and scan through these
directories looking for valid source documents.

The action taken depends on the options passed to the utility.  If no options
are passed, then the default `--build` action will be attempted.  The options
controlling the overall program are described in the sections `Action
options`_ and `Main options`_.  All other options are relegated to the tail of
the manpage, because they are merely configurables for individual document
processors.

The `ldptool` can:

- generate an inventory from multiple source directories (`--sourcedir`)
- crawl through a single output collection (`--pubdir`)
- match the sources to the outputs (based on document stem name)
- describe the collection by type and status (`--summary`)
- list out individual document type and status (`--list`)
- describe supported source formats (`--formats`)
- describe the meaning of document status (`--statustypes`)
- build the expected (non-configurable) set of outputs (`--build`)
- build and publish the outputs (`--publish`)
- produce runnable shell script to STDOUT (`--script`)
- generate configuration files that it can then take as input


Action options
--------------
-h, --help
   show a help message and exit

-b, --build
   Build LDP documentation into the `--builddir` and exit.
   This is the default action if no other action is specified.

-p, --publish
   Build LDP documentation into the `--builddir`.  If all builds are
   successful, then copy the result for each source document into the
   `--pubdir`, effectively replacing (and deleting) the older documents;
   finally, remove `--builddir`, if empty.

-S, --script
   Print a runnable bash script to STDOUT.  This will produce a
   shell script showing what would be executed upon `--build`.

-l, --detail, --list
   Examine the various SOURCEDIRs and the PUBDIR and generate a report
   showing the FORMAT of the source document and STATUS of the document.
   Add the `--verbose` flag for more information.

-t, --summary
   Examine the various SOURCEDIRs and the PUBDIR and generate a short
   report summarizing documents by STATUS and by DOCTYPE.  Add the
   `--verbose` flag for more information.

-T, --doctypes, --formats, --format, --list-doctypes, --list-formats
   List the supported DOCTYPEs; there is one processor for each DOCTYPE.

--statustypes, --list-statustypes
   List the possible document STATUS types.  There are only seven basic status
   types, but several synonyms and groups of STATUS types (internally called
   'classes').

Main options
------------
-s, --sourcedir, --source-dir, --source-directory SOURCEDIR (default: None)
   Specify the name of a SOURCEDIR which contains source documents.  See
   also `Source document discovery`_.

   The `--sourcedir` option may be used more than once.

-o, --pubdir, --output, --outputdir, --outdir PUBDIR (default: None)
   Specify the the name of a PUBDIR.  Used as the publication if the build
   succeeds.  When `--publish` is used with `--pubdir`, the output of
   a successful document build will be used to replace any existing document
   output directory in PUBDIR.

-d, --builddir, --build-dir, --build-directory BUILDDIR (default: 'ldptool-build')
   Specify the name of a BUILDDIR.  A scratch directory used to build each
   source document; directory is temporary and will be removed if the
   build succeeds AND `--publish` has been requested.  Under the `--build` 
   action, all output directories and contents remain in the BUILDDIR for
   inspection.

--verbose [True | False] (default: False)
   Provide more information in --list and --detail actions.  The option can
   be thrown without an argument which is equivalent to True.  To allow the
   CLI to supersede environment or configuration file values, `--verbose
   false` is also supported.

--skip [STEM | DOCTYPE | STATUS]
   Specify a source document name, document type or document status to skip
   during processing.  Each document is known by its STEM (see also `Source
   document discovery`_), its document DOCTYPE (see list below),
   and by the document STATUS (see list below).
   
   The `--skip` option may be used more than once.

   DOCTYPE can be one of: 
     Asciidoc, Docbook4XML, Docbook5XML, DocbookSGML, or Linuxdoc
     (See also output of `--doctypes`)

   STATUS can be one of: 
     source, sources, output, outputs, published, stale, broken, new
     orphan, orphans, orphaned, problems, work, all
     (See also output of `--statustypes`)

--resources RESOURCEDIR (default: ['images', 'resources'])
   Some source documents provide images, scripts and other content.  These
   files are usually stored in a directory such as ./images/ that need to be
   copied intact into the output directory.  Adjust the set of resource
   directories wyth this option.

   The `--resources` option may be used more than once.

--loglevel LOGLEVEL (default: ERROR)
   set the loglevel to LOGLEVEL; can be passed as numeric or textual; in
   increasing order: CRITICAL (50), ERROR (40), WARNING (30), INFO (20),
   DEBUG (10); N.B. the text names are not case-sensitive: 'info' is OK

-c, --configfile, --config-file, --cfg CONFIGFILE (default: None)
   Specify the name of a CONFIGFILE containing parameters to be read for
   this invocation; an INI-style configuration file.  A sample can be
   generated with --dump-cfg.  Although only one CONFIGFILE can be specified
   via the environment or the command-line, the system config file
   (/etc/ldptool/ldptool.ini) is always read.

--dump_cli, --dump-cli
  Produce the resulting, merged configuration as in CLI form.  (After
  processing all configuration sources (defaults, system configuration, user
  configuration, environment variables, command-line.)

--dump_env, --dump-env
  Produce the resulting, merged configuration as a shell environment file.

--dump_cfg, --dump-cfg
  Produce the resulting, merged configuration as an INI-configuration file.

--debug_options, --debug-options
  Provide lots of debugging information on option-processing; see also
  `--loglevel debug`.


Source document discovery
-------------------------
Almost all documentation formats provide the possibility that a document can
span multiple files.  Although more than half of the LDP document collection
consists of single-file HOWTO contributions, there are a number of documents
that are composed of dozens, even hundreds of files.  In order to accommodate
both the simple documents and these much more complex documents, LDP adopted a
simple (unoriginal) naming strategy to allow a single document to span
multiple files::

  Each document is referred to by a stem, which is the filename without any
  extension.  A single file document is simple STEM.EXT.  A document that
  requires many files must be contained in a directory with the STEM name.
  Therefore, the primary source document will always be called either STEM.EXT
  or STEM/STEM.EXT.

(If there is a STEM/STEM.xml and STEM/STEM.sgml in the same directory, that is
an error, and `ldptool` will freak out and shoot pigeons.)

During document discovery, `ldptool` will walk through all of the source
directories specified with `--sourcedir` and build a complete list of all
identifiable source documents.  Then, it will walk through the publication
directory `--pubdir` and match up each output directory (by its STEM) with the
corresponding STEM found in one of the source directories.

Then, `ldptool` can then determine whether any source files are newer.  It uses
content-hashing, i.e. MD5, and if a source file is newer, the status is
`stale`.  If there is no matching output, the source file is `new`.  If
there's an output with no source, that is in `orphan`.  See the
`--statustypes` output for the full list of STATUS types.


Examples
--------
To build and publish a single document::

  $ ldptool --publish DocBook-Demystification-HOWTO
  $ ldptool --publish ~/vcs/LDP/LDP/howto/docbook/Valgrind-HOWTO.xml

To build and publish anything that is new or updated work::

  $ ldptool --publish
  $ ldptool --publish work

To (re-)build and publish everything, regardless of state::

  $ ldptool --publish all

To generate a specific output (into a --builddir)::

  $ ldptool --build DocBook-Demystification-HOWTO

To generate all outputs into a --builddir (should exist)::

  $ ldptool --builddir ~/tmp/scratch-directory/ --build all

To build new/updated work, but pass over a trouble-maker::

  $ ldptool --build --skip HOWTO-INDEX

To loudly generate all outputs, except a trouble-maker::

  $ ldptool --build all --loglevel debug --skip HOWTO-INDEX

To print out a shell script for building a specific document::

  $ ldptool --script TransparentProxy
  $ ldptool --script ~/vcs/LDP/LDP/howto/docbook/Assembly-HOWTO.xml


Environment
-----------

The `ldptool` accepts configuration via environment variables.  All such
environment variables are prefixed with the name `LDPTOOL_`.

The name of each variable is constructed from the primary
command-line option name.  The `-b` is better known as `--builddir`, so the
environment variable would be `LDPTOOL_BUILDDIR`.  Similarly, the environment
variable names for each of the handlers can be derived from the name of the
handler and its option.  For example, the Asciidoc processor needs to have
access to the `xmllint` and `asciidoc` utilities.  

The environment variable corresponding to the CLI option `--asciidoc-xmllint`
would be `LDPTOOL_ASCIIDOC_XMLLINT`.  Similarly, `--asciidoc-asciidoc` should
be `LDPTOOL_ASCIIDOC_ASCIIDOC`.

Variables accepting multiple options use the comma as a separator::

  LDPTOOL_RESOURCES=images,resources

The complete listing of possible environment variables with all current values
can be printed by using `ldptool --dump-env`.  

Configuration file
------------------
The system-installed configuration file is `/etc/ldptool/ldptool.ini`.  The
format is a simple INI-style configuration file with a block for the main
program and a block for each handler.  Here's a partial example::

  [ldptool] 
  resources = images,
          resources
  loglevel = 40
  
  [ldptool-asciidoc]
  asciidoc = /usr/bin/asciidoc
  xmllint = /usr/bin/xmllint

Note that the comma separates multiple values for a single option
(`resources`) in the above config fragment.

The complete, current configuration file can be printed by using `ldptool
--dump-cfg`.  


Configuration option fragments for each DOCTYPE handler
-------------------------------------------------------
Every source format has a single handler and each DOCTYPE handler may require
a different set of executables and/or data files to complete its job.  The
defaults depend on the platform and are detected at runtime.  In most cases,
the commands are found in `/usr/bin` (see below).  The data files, for example
the LDP XSL files and the docbook.rng, may live in different places on
different systems.

If a given DOCTYPE handler cannot find all of its requirements, it will
complain to STDERR during execution, but will not abort the rest of the run.

If, for some reason, `ldptool` cannot find data files, but you know where they
are, consider generating a configuration file with the `--dump-cfg` option,
adjusting the relevant options and then passing the `--configfile your.ini` to
specify these paths.


Asciidoc
--------
--asciidoc-asciidoc PATH
  full path to asciidoc [/usr/bin/asciidoc]
--asciidoc-xmllint PATH
  full path to xmllint [/usr/bin/xmllint]

N.B. The Asciidoc processor simply converts the source document to a
Docbook4XML document and then uses the richer Docbook4XML toolchain.

Docbook4XML
-----------
--docbook4xml-xslchunk PATH
  full path to LDP HTML chunker XSL
--docbook4xml-xslsingle PATH
  full path to LDP HTML single-page XSL
--docbook4xml-xslprint PATH
  full path to LDP FO print XSL
--docbook4xml-xmllint PATH
  full path to xmllint [/usr/bin/xmllint]
--docbook4xml-xsltproc PATH
  full path to xsltproc [/usr/bin/xsltproc]
--docbook4xml-html2text PATH
  full path to html2text [/usr/bin/html2text]
--docbook4xml-fop PATH
  full path to fop [/usr/bin/fop]
--docbook4xml-dblatex PATH
  full path to dblatex [/usr/bin/dblatex]

Docbook5XML
-----------
--docbook5xml-xslchunk PATH
  full path to LDP HTML chunker XSL
--docbook5xml-xslsingle PATH
  full path to LDP HTML single-page XSL
--docbook5xml-xslprint PATH
  full path to LDP FO print XSL
--docbook5xml-rngfile PATH
  full path to docbook.rng
--docbook5xml-xmllint PATH
  full path to xmllint [/usr/bin/xmllint]
--docbook5xml-xsltproc PATH
  full path to xsltproc [/usr/bin/xsltproc]
--docbook5xml-html2text PATH
  full path to html2text [/usr/bin/html2text]
--docbook5xml-fop PATH
  full path to fop [/usr/bin/fop]
--docbook5xml-dblatex PATH
  full path to dblatex [/usr/bin/dblatex]
--docbook5xml-jing PATH
  full path to jing [/usr/bin/jing]

DocbookSGML
-----------
--docbooksgml-docbookdsl PATH
  full path to html/docbook.dsl
--docbooksgml-ldpdsl PATH
  full path to ldp/ldp.dsl [None]
--docbooksgml-jw PATH
  full path to jw [/usr/bin/jw]
--docbooksgml-html2text PATH
  full path to html2text [/usr/bin/html2text]
--docbooksgml-openjade PATH
  full path to openjade [/usr/bin/openjade]
--docbooksgml-dblatex PATH
  full path to dblatex [/usr/bin/dblatex]
--docbooksgml-collateindex PATH
  full path to collateindex

Linuxdoc
--------
--linuxdoc-sgmlcheck PATH
  full path to sgmlcheck [/usr/bin/sgmlcheck]
--linuxdoc-sgml2html PATH
  full path to sgml2html [/usr/bin/sgml2html]
--linuxdoc-html2text PATH
  full path to html2text [/usr/bin/html2text]
--linuxdoc-htmldoc PATH
  full path to htmldoc [/usr/bin/htmldoc]

