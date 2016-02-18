#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
import errno
import collections

from .utils import logger, statfiles
from .typeguesser import guess, knownextensions


class SourceCollection(collections.MutableMapping):

    def __repr__(self):
        return '<%s:(%s docs)>' % (self.__class__.__name__, len(self))

    def __init__(self, args=None):
        if args is None:
            return
        dirs = [os.path.abspath(x) for x in args]
        results = [os.path.exists(x) for x in dirs]

        if not all(results):
            for result, sdir in zip(results, dirs):
                logger.critical("Directory does not exist: " + sdir)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), sdir)

        for sdir in dirs:
            for fname in os.listdir(sdir):
                candidates = list()
                possible = os.path.join(sdir, fname)
                if os.path.isfile(possible):
                    candidates.append(SourceDocument(possible))
                elif os.path.isdir(possible):
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
                        logger.warning("Ignoring duplicate is %s", candy.filename)
                        logger.warning("Existing dup-entry is %s", self[candy.stem].filename)
                    else:
                        self[candy.stem] = candy
        logger.debug("Discovered %s documents total", len(self))

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

        self.doctype = self._doctype()
        self.status = 'source'
        self.dirname, self.basename = os.path.split(self.filename)
        self.stem, self.ext = os.path.splitext(self.basename)
        parentbase = os.path.basename(self.dirname)
        logger.debug("%s found source %s", self.stem, self.filename)
        if parentbase == self.stem:
            self.statinfo = statfiles(self.dirname, relative=self.dirname)
        else:
            self.statinfo = statfiles(self.filename, relative=self.dirname)

    def _doctype(self):
        return guess(self.filename)

#
# -- end of file
