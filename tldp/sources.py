#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
import operator

from .utils import logger
from .guess import guess, knownextensions


class Sources(object):

    def __repr__(self):
        return '<%s:(%s docs)>' % \
               (self.__class__.__name__, len(self.docs))

    def __init__(self, args):
        self.sourcedirs = [os.path.abspath(x) for x in args]
        self.docs = list()
        self.validateDirs()
        self.enumerateDocuments()
        self.docs.sort(key=operator.attrgetter('stem'))

    def validateDirs(self):
        results = [os.path.exists(x) for x in self.sourcedirs]
        if not all(results):
            for result, sdir in zip(results, self.sourcedir):
                logger.critical("[Errno 2] No such file or directory: " + sdir)
            raise OSError("[Errno 2] No such file or directory: " + sdir)

    def enumerateDocuments(self):
        for sdir in self.sourcedirs:
            docs = list()
            for fname in os.listdir(sdir):
                possible = os.path.join(sdir, fname)
                if os.path.isfile(possible):
                    docs.append(SourceDocument(possible))
                elif os.path.isdir(fname):
                    stem = os.path.basename(fname)
                    for ext in knownextensions:
                        possible = os.path.join(sdir, fname, stem + ext)
                        if os.path.isfile(possible):
                            docs.append(SourceDocument(possible))
            logger.debug("Discovered %s documents in %s", len(docs), sdir)
            self.docs.extend(docs)
        logger.info("Discovered %s documents total", len(self.docs))


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
        self.dirname, self.basename = os.path.split(self.filename)
        self.stem, self.ext = os.path.splitext(self.basename)
        self.stat = os.stat(self.filename)

        self.resources = False  # -- assume no ./images/, ./resources/
        self.singlefile = True  # -- assume only one file
        parentdir = os.path.basename(self.dirname)
        if parentdir == self.stem:
            self.singlefile = False
            for rdir in ('resources', 'images'):
                if os.path.exists(os.path.join(self.dirname, rdir)):
                    self.resources = True

    @property
    def doctype(self):
        return guess(self.filename)

# -- end of file
