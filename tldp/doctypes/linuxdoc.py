#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os

from ..utils import logger, execute
from .common import BaseDoctype, SignatureChecker


class Linuxdoc(BaseDoctype, SignatureChecker):
    formatname = 'Linuxdoc'
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]
    tools = ['sgml2html', 'html2text', 'htmldoc']

    # def __init__(self, *args, **kwargs):
    #     self.source = kwargs.get('source')
    #     self.output = kwargs.get('output')
    #     self.platform = kwargs.get('platform')
    #     super(Linuxdoc, self).__init__()

    def platform_check(self):
        for tool in self.tools:
            assert hasattr(self.platform, tool)

    def create_txt(self):
        logger.info("%s creating TXT.", self.source.stem)
        cmd = [self.platform.html2text, '-style', 'pretty', '-nobs',
               self.output.name_htmls]
        stdout = open(self.output.name_txt, 'wx')
        result = execute(cmd, logdir=self.logdir, stdout=stdout)
        if result == 0:
            return os.path.isfile(self.output.name_txt)
        else:
            return False

    def create_pdf(self):
        logger.info("%s creating PDF.", self.source.stem)
        cmd = [self.platform.htmldoc, '--size', 'universal', '-t', 'pdf',
               '--firstpage', 'p1', '--outfile', self.output.name_pdf,
               self.output.name_htmls]
        result = execute(cmd, logdir=self.logdir)
        if result == 0:
            return os.path.isfile(self.output.name_pdf)
        else:
            return False

    def create_html(self):
        stem = self.source.stem
        logger.info("%s creating chunked HTML.", stem)
        cmd = [self.platform.sgml2html, self.source.filename]
        result = execute(cmd, logdir=self.logdir)
        if result == 0:  # -- only symlink, if HTML generated successfully
            target = os.path.basename(self.output.name_html)
            logger.debug("%s creating index.html symlink to %s.", stem, target)
            try:
                os.symlink(target, 'index.html')
            except OSError:
                logger.debug("%s failed in creating index.html symlink.", stem)
        return os.path.isfile(self.output.name_html)

    def create_htmls(self):
        stem = self.source.stem
        logger.info("%s creating single-file HTML.", stem)
        cmd = [self.platform.sgml2html, '--split=0', self.source.filename]
        result = execute(cmd, logdir=self.logdir)
        logger.debug("%s result %r.",  stem, result)
        if result == 0:  # -- only rename, if HTML generated successfully
            target = os.path.basename(self.output.name_htmls)
            logger.debug("%s renaming HTML single file to %s.", stem, target)
            try:
                os.rename(self.output.name_html, self.output.name_htmls)
            except OSError:
                logger.debug("%s failed renaming HTML single file to %s.", stem, target)
        return os.path.isfile(self.output.name_htmls)

#
# -- end of file
