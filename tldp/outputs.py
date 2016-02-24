#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import sys
import errno
import shutil

from tldp.ldpcollection import LDPDocumentCollection
from tldp.utils import logger, logdir, statfiles


class OutputNamingConvention(object):
    '''A base class inherited by OutputDirectory to ensure consistent
    naming of files across the output collection of documents,
    regardless of the source document type and processing toolchain
    choice.

    Sets a list of names for documents that are expected to be present
    in order to report that the directory iscomplete.
    '''
    expected = ['name_txt', 'name_pdf', 'name_htmls', 'name_html',
                'name_indexhtml']

    def __init__(self, dirname, stem):
        self.dirname = dirname
        self.stem = stem

    @property
    def name_txt(self):
        return os.path.join(self.dirname, self.stem + '.txt')

    @property
    def name_fo(self):
        return os.path.join(self.dirname, self.stem + '.fo')

    @property
    def name_pdf(self):
        return os.path.join(self.dirname, self.stem + '.pdf')

    @property
    def name_html(self):
        return os.path.join(self.dirname, self.stem + '.html')

    @property
    def name_htmls(self):
        return os.path.join(self.dirname, self.stem + '-single.html')

    @property
    def name_epub(self):
        return os.path.join(self.dirname, self.stem + '.epub')

    @property
    def name_indexhtml(self):
        return os.path.join(self.dirname, 'index.html')

    @property
    def iscomplete(self):
        '''True if the output directory contains all expected documents'''
        present = list()
        for prop in self.expected:
            name = getattr(self, prop, None)
            assert name is not None
            present.append(os.path.isfile(name))
        return all(present)

    @property
    def missing(self):
        '''returns a set of missing files'''
        missing = set()
        for prop in self.expected:
            name = getattr(self, prop, None)
            assert name is not None
            if not os.path.isfile(name):
                missing.add(name)
        return missing


class OutputDirectory(OutputNamingConvention):
    '''A class providing a container for each set of output documents
    for a given source document and general methods for operating on
    and preparing the output directory for a document processor.
    For example, the process of generating each document type for a single
    source (e.g. 'Unicode-HOWTO') would be managed by this object.

    An important element of the OutputDirectory is the stem, determined
    from the directory name when __init__() is called.
    '''
    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.dirname)

    def __init__(self, dirname):
        '''constructor
        :param dirname: directory name for all output documents

        This directory name is expected to end with the document stem name,
        for example '/path/to/the/collection/Unicode-HOWTO'.  The parent
        directory (e.g. '/path/to/the/collection' must exist already.  The
        output directory itself will be created, or emptied and cleared if
        the document needs to be rebuilt.
        '''
        self.dirname = os.path.abspath(dirname)
        self.stem = os.path.basename(self.dirname)
        super(OutputDirectory, self).__init__(self.dirname, self.stem)
        parent = os.path.dirname(self.dirname)
        if not os.path.isdir(parent):
            logger.critical("Missing output collection directory %s.", parent)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), parent)
        self.statinfo = statfiles(self.dirname, relative=self.dirname)
        self.status = 'output'
        self.source = None
        self.logdir = os.path.join(self.dirname, logdir)

    def clean(self):
        '''remove the output directory for this document

        This is done as a matter of course when the output documents must be
        regenerated.  Better to start fresh.
        '''
        logger.debug("%s removing dir   %s.", self.stem, self.dirname)
        if os.path.isdir(self.dirname):
            shutil.rmtree(self.dirname)

    def hook_prebuild(self):
        self.clean()
        for d in (self.dirname, self.logdir):
            if not os.path.isdir(d):
                logger.debug("%s creating dir   %s.", self.stem, d)
                os.mkdir(d)
        #self.copy_ancillaries(self.dirname)
        return True

    def hook_build_failure(self):
        logger.error("%s FAILURE, see logs in %s", self.stem, self.logdir)
        return True

    def hook_build_success(self):
        logger.info("%s build success  %s.", self.stem, self.dirname)
        logger.debug("%s removing logs  %s)", self.stem, self.logdir)
        if os.path.isdir(self.logdir):
            shutil.rmtree(logdir)
        return True

    def detail(self, widths, verbose, file=sys.stdout):
        '''
        '''
        template = '{s.status:{w.status}} {s.stem:{w.stem}}'
        outstr = template.format(s=self, w=widths)
        print(outstr)
        if verbose:
            pass


class OutputCollection(LDPDocumentCollection):
    '''a dict-like container for OutputDirectory objects

    The key of an OutputCollection is the stem name of the document, which
    allows convenient access and guaranteed non-collision.

    The use of the stem as a key works conveniently with the
    SourceCollection which uses the same strategy on SourceDocuments.
    '''
    def __init__(self, dirname=None):
        '''construct an OutputCollection

        If dirname is not supplied, OutputCollection is basically, a dict().
        If dirname is supplied, then OutputCollection scans the filesystem
        for subdirectories of dirname and creates an OutputDirectory for each
        subdir.  Each subdir name is used as the stem (or key) for holding the
        OutputDirectory in the OutputCollection.

        For example, consider the following directory tree:

            en
            ├── Latvian-HOWTO
            ├── Scanner-HOWTO
            ├── UUCP-HOWTO
            └── Wireless-HOWTO

        If called like OutputCollection("en"), the result in memory would be
        a structure resembling this:

            OutputCollection("/path/en") = {
              "Latvian-HOWTO":  OutputDirectory("/path/en/Latvian-HOWTO")
              "Scanner-HOWTO":  OutputDirectory("/path/en/Scanner-HOWTO")
              "UUCP-HOWTO":     OutputDirectory("/path/en/UUCP-HOWTO")
              "Wireless-HOWTO": OutputDirectory("/path/en/Wireless-HOWTO")
              }

        '''
        if dirname is None:
            return
        elif not os.path.isdir(dirname):
            logger.critical("Output collection dir %s must already exist.",
                            dirname)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), dirname)
        for fname in sorted(os.listdir(dirname)):
            name = os.path.join(dirname, fname)
            if not os.path.isdir(name):
                logger.info("Skipping non-directory %s (in %s)", name, dirname)
                continue
            logger.debug("Found directory %s (in %s)", name, dirname)
            o = OutputDirectory(name)
            assert o.stem not in self
            self[o.stem] = o


#
# -- end of file
