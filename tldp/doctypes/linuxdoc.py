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
        return True

    def create_txt(self):
        exe = self.platform.html2text
        inf = self.output.name_htmls
        assert os.path.exists(inf)
        outf = self.output.name_txt
        stem = self.source.stem
        cmd = [exe, '-style', 'pretty', '-nobs', inf]
        logger.debug("%s creating TXT %s.", stem, outf)
        stdout = open(outf, 'wx')
        result = execute(cmd, logdir=self.logdir, stdout=stdout)
        if result == 0:
            logger.info("%s created TXT %s.", stem, outf)
            return os.path.isfile(outf)
        return False

    def create_pdf(self):
        exe = self.platform.htmldoc
        inf = self.output.name_htmls
        assert os.path.exists(inf)
        outf = self.output.name_pdf
        stem = self.source.stem
        logger.info("%s creating PDF %s.", stem, outf)
        cmd = [exe, '--size', 'universal', '-t', 'pdf', '--firstpage', 'p1',
               '--outfile', outf, inf]
        result = execute(cmd, logdir=self.logdir)
        if result == 0:
            logger.info("%s created PDF %s.", stem, outf)
            return os.path.isfile(outf)
        return False

    def create_html(self):
        exe = self.platform.sgml2html
        inf = self.source.filename
        assert os.path.exists(inf)
        outf = self.output.name_html
        stem = self.source.stem
        logger.info("%s creating chunked HTML %s, etc.", stem, outf)
        cmd = [exe, inf]
        result = execute(cmd, logdir=self.logdir)
        if result == 0:  # -- only symlink, if HTML generated successfully
            target = os.path.basename(outf)
            logger.debug("%s creating index.html symlink to %s.", stem, target)
            try:
                os.symlink(target, 'index.html')
            except OSError:
                logger.debug("%s failed in creating index.html symlink.", stem)
        return os.path.isfile(outf)

    def create_htmls(self):
        exe = self.platform.sgml2html
        inf = self.source.filename
        assert os.path.exists(inf)
        outf = self.output.name_htmls
        stem = self.source.stem
        logger.info("%s creating single-file HTML %s, etc.", stem, outf)
        cmd = [exe, '--split=0', inf]
        result = execute(cmd, logdir=self.logdir)
        if result == 0:  # -- only rename, if HTML generated successfully
            source = os.path.basename(self.output.name_html)
            target = os.path.basename(self.output.name_htmls)
            logger.debug("%s renaming HTML single file to %s.", stem, target)
            try:
                os.rename(source, target)
            except OSError:
                logger.debug("%s failed renaming HTML single file to %s.",
                             stem, target)
        return os.path.isfile(outf)

#
# -- end of file
