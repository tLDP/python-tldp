#! /usr/bin/python

from __future__ import print_function

import os
import sys
import logging

from .utils import logger
from .guess import guess, knownextensions


class SourceDir(object):

    def __repr__(self):
        return '<%s:%s (%s docs)>' % \
               (self.__class__.__name__, self.sourcedir, len(self.docs))

    def __init__(self, sourcedir):
        self.sourcedir = os.path.abspath(sourcedir)
        self.docs = list()
        if not os.path.exists(sourcedir):
            raise OSError("[Errno 2] No such file or directory: " + sourcedir)
        self.enumerateDocuments()

    def enumerateDocuments(self):
        for fname in os.listdir(self.sourcedir):
            possible = os.path.join(self.sourcedir, fname)
            if os.path.isfile(possible):
                self.docs.append(SourceDocument(possible))
            elif os.path.isdir(fname):
                stem = os.path.basename(fname)
                for ext in knownextensions:
                    possible = os.path.join(self.sourcedir, fname, stem + ext)
                    if os.path.isfile(possible):
                        self.docs.append(SourceDocument(possible))
        logger.info("Discovered %s documents in %s",
                    len(self.docs), self.sourcedir)


class SourceDocument(object):

    def __repr__(self):
        return '<%s:%s (%s)>' % \
               (self.__class__.__name__, self.filename, self.doctype)

    def __init__(self, filename):
        # -- canonicalize the pathname we are given.
        self.filename = os.path.abspath(filename)
        if not os.path.exists(self.filename):
            raise OSError("Missing source document: " + self.filename)

        logger.debug("Found existing %s", self.filename)
        self.sourcedir, self.basename = os.path.split(self.filename)
        self.stem, self.ext = os.path.splitext(self.basename)
        self.stat = os.stat(self.filename)

        self.resources = False  # -- assume no ./images/, ./resources/
        self.singlefile = True  # -- assume only one file
        parentdir = os.path.basename(self.sourcedir)
        if parentdir == self.stem:
            self.singlefile = False
            for rdir in ('resources', 'images'):
                if os.path.exists(os.path.join(self.sourcedir, rdir)):
                    self.resources = True

    @property
    def doctype(self):
        return guess(self.filename)

# -- end of file
