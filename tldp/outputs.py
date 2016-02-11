#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os

from .utils import logger


class OutputDir(object):

    def __init__(self, outputdir):
        self.outputdir = os.path.abspath(outputdir)
        self.stem = os.path.basename(outputdir)
        self.parent = os.path.dirname(self.outputdir)

    def mkdir(self):
        if not os.path.exists(self.parent):
            raise OSError("Missing parent directory: " + self.parent)
        os.mkdir(self.outputdir)

    @property
    def txt_name(self):
        return os.path.join(self.outputdir, self.stem, '.txt')

    @property
    def pdf_name(self):
        return os.path.join(self.outputdir, self.stem, '.pdf')

    @property
    def html_name(self):
        return os.path.join(self.outputdir, self.stem, '.html')

    @property
    def htmls_name(self):
        return os.path.join(self.outputdir, self.stem, '-single.html')


# -- end of file
