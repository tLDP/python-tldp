#! /usr/bin/python

from __future__ import print_function

import os

from .utils import logger


class OutputDir(object):

    def __init__(self, dirname):
        self.dirname = os.path.abspath(dirname)
        self.stem = os.path.basename(dirname)
        self.members = list()

    def mkdir(self):
        if not os.path.exists(self.parent):
            raise OSError("Missing parent directory: " + self.parent)
        os.mkdir(self.dirname)

    @property
    def txt_name(self):
        return os.path.join(self.dirname, self.stem, '.txt')

    @property
    def pdf_name(self):
        return os.path.join(self.dirname, self.stem, '.pdf')

    @property
    def html_name(self):
        return os.path.join(self.dirname, self.stem, '.html')

    @property
    def htmls_name(self):
        return os.path.join(self.dirname, self.stem, '-single.html')


# -- end of file
