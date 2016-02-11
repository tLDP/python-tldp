#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os

from ..utils import logger, runner
from .common import SignatureChecker


class Linuxdoc(SignatureChecker):
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]

    def __init__(self, source, output, runner):
        self.source = source
        self.output = output
        self.runner = runner

    def create_txt(self):
        cmd = ['html2text', '-style', 'pretty', '-nobs',
               self.output.htmls_name]
        stdout = self.output.txt_name

    def create_pdf(self):
        cmd = ['htmldoc', '--size', 'universal', '-t', 'pdf',
               '--firstpage', 'p1', '--outfile', self.output.pdf_name,
               self.output.htmls_name]

    def create_html(self):
        success = False
        try:
            cmd = ['sgml2html', self.source.filename]

        except OSError:
            success = False
        try:
            opwd = os.getcwd()
            os.chdir(self.output.dirname)
            os.symlink(os.path.basename(self.output.html_name), 'index.html')
            os.chdir(opwd)
            success = True
        except OSError:
            success = False
        return success

    def create_htmls(self):
        cmd = ['sgml2html', '--split=0', self.source.filename]
        os.rename(self.output.html_name, self.output.htmls_name)

#
# -- end of file
