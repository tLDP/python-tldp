#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os

from ..utils import logger
from .common import SignatureChecker


class Linuxdoc(SignatureChecker):
    formatname = 'Linuxdoc'
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]
    tools = ['sgml2html', 'html2text', 'htmldoc']

    def __init__(self, *args, **kwargs):
        self.source = kwargs.get('source')
        self.output = kwargs.get('output')
        super(Linuxdoc, self).__init__()

    def create_txt(self):
        cmd = [self.html2text, '-style', 'pretty', '-nobs',
               self.output.htmls_name]
        stdout = self.output.txt_name

    def create_pdf(self):
        logger.info("Creating PDF for %s", self.source.stem)
        cmd = [self.htmldoc, '--size', 'universal', '-t', 'pdf',
               '--firstpage', 'p1', '--outfile', self.output.pdf_name,
               self.output.htmls_name]

    def create_html(self):
        logger.info("Creating chunked HTML for %s", self.source.stem)
        cmd = [self.sgml2html, self.source.filename]
        try:
            # -- execute cmd
            pass
        except OSError:
            return False

        success = False
        try:
            opwd = os.getcwd()
            os.chdir(self.output.dirname)
            os.symlink(os.path.basename(self.output.html_name), 'index.html')
            os.chdir(opwd)
            success = True
        except OSError:
            pass
        return success

    def create_htmls(self):
        cmd = [self.sgml2html, '--split=0', self.source.filename]
        os.rename(self.output.html_name, self.output.htmls_name)

#
# -- end of file
