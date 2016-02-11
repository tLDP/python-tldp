#! /usr/bin/python

from __future__ import print_function

import os

from ..utils import logger
from ..outputs import OutputDir
from .common import SignatureChecker


class Linuxdoc(SignatureChecker, OutputDir):
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]

    def __init__(self):
        pass

    def create_txt(self):
        cmd = ['html2text', '-style', 'pretty', '-nobs', 
               self.htmls_name]
        stdout = self.txt_name

    def create_pdf(self):
        cmd = ['htmldoc', '--size', 'universal', '-t', 'pdf', 
               '--firstpage', 'p1', '--outfile', self.pdf_name,
               self.htmls_name]

    def create_html(self):
        cmd = ['sgml2html', self.filename]
        os.symlink(self.html_name, 'index.html')

    def create_htmls(self):
        cmd = ['sgml2html', '--split=0', self.filename]
        os.rename(self.html_name, self.htmls_name)

#
# -- end of file
