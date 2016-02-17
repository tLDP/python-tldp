#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
import errno

import collections
from .utils import logger, statfiles


class OutputNamingConvention(object):

    expected = ['name_txt', 'name_pdf', 'name_htmls', 'name_html',
                'name_index']

    def __init__(self, dirname, stem):
        self.dirname = dirname
        self.stem = stem

    @property
    def name_txt(self):
        return os.path.join(self.dirname, self.stem + '.txt')

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
    def name_index(self):
        return os.path.join(self.dirname, 'index.html')


class OutputDirectory(OutputNamingConvention):

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.dirname)

    def __init__(self, dirname):
        self.dirname = os.path.abspath(dirname)
        self.stem = os.path.basename(self.dirname)
        parent = os.path.dirname(self.dirname)
        if not os.path.isdir(parent):
            logger.critical("Missing output tree %s.", parent)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), parent)
        if not os.path.isdir(self.dirname):
            logger.info("%s creating output directory %s.", self.stem, dirname)
            os.mkdir(dirname)
        self.statinfo = statfiles(self.dirname, relative=self.dirname)
        self.status = 'output'
        super(OutputDirectory, self).__init__(self.dirname, self.stem)

    def clean(self):
        logger.info("%s cleaning directory %s.", self.stem, self.dirname)
        for oformat in self.expected:
            name = getattr(self, oformat, None)
            assert name is not None
            if os.path.exists(name) or os.path.islink(name):
                logger.info("%s cleaning directory %s, removing file %s",
                            self.stem, self.dirname, os.path.basename(name))
                os.unlink(name)
        return True


class OutputCollection(collections.MutableMapping):

    def __repr__(self):
        return '<%s:(%s docs)>' % (self.__class__.__name__, len(self))

    def __init__(self, dirname=None):
        if dirname is None:
            return
        elif not os.path.isdir(dirname):
            logger.critical("Directory %s must already exist.", dirname)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), dirname)
        for fname in os.listdir(dirname):
            name = os.path.join(dirname, fname)
            if not os.path.isdir(name):
                logger.info("Skipping non-directory %s (in %s)", name, dirname)
                continue
            o = OutputDirectory(name)
            assert o.stem not in self
            self[o.stem] = o

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

#
# -- end of file
