#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
import errno

from .utils import logger


class OutputNamingConvention(object):

    expected = ['name_txt', 'name_pdf', 'name_htmls', 'name_html',
                'name_index']

    def __init__(self, stem, dirname):
        self.stem = stem
        self.dirname = dirname

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

    def __init__(self, dirname):
        self.dirname = os.path.abspath(dirname)
        self.stem = os.path.basename(self.dirname)
        parent = os.path.dirname(self.dirname)
        if not os.path.isdir(parent):
            logger.critical("Missing output tree %s.", parent)
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), parent)
        if not os.path.isdir(self.dirname):
            logger.info("Creating output directory %s.", dirname)
            os.mkdir(dirname)
        super(OutputDirectory, self).__init__(self.stem, self.dirname)

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


class OutputTree(object):

    def __repr__(self):
        return '<%s:(%s docs)>' % \
               (self.__class__.__name__, len(self.docs))

    def __init__(self, dirname):
        if not os.path.isdir(dirname):
            logger.critical("Directory %s must already exist.", dirname)
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), dirname)
        self.dirname = dirname
        self.docs = dict()
        self.enumerateDocuments()

    def enumerateDocuments(self):
        for fname in os.listdir(self.dirname):
            name = os.path.join(self.dirname, fname)
            if not os.path.isdir(name):
                logger.warning("Skipping non-directory %s (in %s)",
                               name, self.dirname)
            o = OutputDirectory(name)
            assert not self.docs.has_key(o.stem)
            self.docs[o.stem] = o


#
# -- end of file
