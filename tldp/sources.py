#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
import errno
import collections

from .utils import logger
from .typeguesser import guess, knownextensions


class SourceCollection(collections.MutableMapping):

    def __repr__(self):
        return '<%s:(%s docs)>' % \
               (self.__class__.__name__, len(self))

    def __init__(self, args):
        dirs = [os.path.abspath(x) for x in args]
        results = [os.path.exists(x) for x in dirs]

        if not all(results):
            for result, sdir in zip(results, dirs):
                logger.critical("Directory does not exist: " + sdir)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), sdir)

        for sdir in dirs:
            docs = dict()
            candidates = list()
            for fname in os.listdir(sdir):
                possible = os.path.join(sdir, fname)
                if os.path.isfile(possible):
                    candidates.append(SourceDocument(possible))
                elif os.path.isdir(fname):
                    stem = os.path.basename(fname)
                    for ext in knownextensions:
                        possible = os.path.join(sdir, fname, stem + ext)
                        if os.path.isfile(possible):
                            candidates.append(SourceDocument(possible))
                else:
                    logger.warning("Skipping non-directory, non-plain file %s",
                                   possible)
                    continue
                for candy in candidates:
                    if candy.stem in self:
                        logger.warning("Duplicate stems: %s and %s", 
                                        self[candy.stem].filename, candy.filename)
                        logger.warning("Ignoring %s", candy.filename)
                    else:
                        self[candy.stem] = candy
        logger.info("Discovered %s documents total", len(self))

    def __delitem__(self, key):
        del self.__dict__[key]

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class SourceDocument(object):

    def __repr__(self):
        return '<%s:%s (%s)>' % \
               (self.__class__.__name__, self.filename, self.doctype)

    def __init__(self, filename):
        # -- canonicalize the pathname we are given.
        self.filename = os.path.abspath(filename)
        if not os.path.exists(self.filename):
            logger.critical("Missing source document: %s", self.filename)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), self.filename)
        if not os.path.isfile(self.filename):
            logger.critical("Source document is not a plain file: %s", self.filename)
            raise TypeError("Wrong type, not a plain file: " + self.filename)

        logger.debug("Found existing %s", self.filename)
        self.doctype = self._doctype()
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

    def _doctype(self):
        return guess(self.filename)

#
# -- end of file
