#! /usr/bin/python

from __future__ import print_function

import os
import sys
import logging

from .utils import logger
from .guess import knownextensions

# class SourceTree(object):
#
#     def __init__(self, root, config):
#         pass


class SourceDir(object):

    def __repr__(self):
        return self.dirname

    def __init__(self, dirname):
        self.dirname = os.path.abspath(dirname)
        self.docs = list()
        if not os.path.exists(dirname):
            raise OSError("[Errno 2] No such file or directory: " + dirname)
        logger.info("Time to go for an enumeration stroll in %s", dirname)
        self.enumerateDocuments()

    def enumerateDocuments(self):
        for fname in os.listdir(self.dirname):
            possible = os.path.join(self.dirname, fname)
            if os.path.isfile(possible):
                self.docs.append(SourceDocument(possible))
            elif os.path.isdir(fname):
                stem = os.path.basename(fname)
                for ext in knownextensions:
                    possible = os.path.join(self.dirname, fname, stem + ext)
                    if os.path.isfile(possible):
                        self.docs.append(SourceDocument(possible))
        logger.info("Discovered %s documents in %s",
                    len(self.docs), self.dirname)


class SourceDocument(object):

    def __repr__(self):
        return self.filename

    def __init__(self, filename):
        # -- canonicalize the pathname we are given.
        self.filename = os.path.abspath(filename)
        if not os.path.exists(self.filename):
            raise OSError("Missing source document: " + self.filename)

        self.dirname, self.basename = os.path.split(self.filename)
        self.stem, self.ext = os.path.splitext(self.basename)
        self.stat = os.stat(self.filename)

        self.doctype = None
        self.resources = False  # -- assume no ./images/, ./resources/
        self.singlefile = True  # -- assume only one file
        parentdir = os.path.basename(self.dirname)
        if parentdir == self.stem:
            self.singlefile = False
            for rdir in ('resources', 'images'):
                if os.path.exists(os.path.join(self.dirname, rdir)):
                    self.resources = True

    def doctype(self):
        if self.doctype is None:
            self.doctype = guess(self.filename)
        return self.doctype


class OutputDocument(object):

    formats = {'pdf':  '.pdf',
               'txt':  '.txt',
               'html':  '.html',
               'htmls':  '-single.html', }

    def __init__(self, filename):
        pass

    @property
    def txt(self):
        return os.path.join(self.dirname, self.stem, '.txt')


class OutputDir(object):

    def __init__(self, dirname):
        self.dirname = os.path.abspath(dirname)
        self.parent = os.path.dirname(dirname)
        self.stem = os.path.basename(dirname)
        self.members = list()

    def mkdir(self):
        if not os.path.exists(self.parent):
            raise OSError("Missing parent directory: " + self.parent)
        os.mkdir(self.dirname)
        return os.path.exists(self.dirname)

    @property
    def members(self):
        return os.path.exists(self.dirname)

    @property
    def exists(self):
        return os.path.exists(self.dirname)

    @property
    def isComplete(self):
        return all(self.pdf, self.html, self.htmls, self.txt)

# -- end of file
