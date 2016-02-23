#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os

from tldp.utils import logger, which, execute
from tldp.utils import arg_isexecutable, isexecutable
from tldp.doctypes.common import BaseDoctype, SignatureChecker


def config_fragment(p):
    p.add_argument('--linuxdoc-sgml2html', type=arg_isexecutable,
                   default=which('sgml2html'),
                   help='full path to sgml2html [%(default)s]')
    p.add_argument('--linuxdoc-html2text', type=arg_isexecutable,
                   default=which('html2text'),
                   help='full path to html2text [%(default)s]')
    p.add_argument('--linuxdoc-htmldoc', type=arg_isexecutable,
                   default=which('htmldoc'),
                   help='full path to htmldoc [%(default)s]')


class Linuxdoc(BaseDoctype, SignatureChecker):
    formatname = 'Linuxdoc'
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]

    required = {'linuxdoc_sgml2html': isexecutable,
                'linuxdoc_html2text': isexecutable,
                'linuxdoc_htmldoc': isexecutable,
                }

    def build_precheck(self):
        for tool, validator in self.required.items():
            thing = getattr(self.config, tool, None)
            assert thing is not None
            assert validator(thing)
        return True

    def create_txt(self):
        exe = self.config.linuxdoc_html2text
        inf = self.output.name_htmls
        assert os.path.exists(inf)
        outf = self.output.name_txt
        stem = self.source.stem
        logdir = self.output.logdir
        cmd = [exe, '-style', 'pretty', '-nobs', inf]
        logger.debug("%s creating TXT   %s.", stem, outf)
        with open(outf, 'wx') as stdout:
            result = execute(cmd, logdir=logdir, stdout=stdout)
        if result != 0:
            return False
        logger.info("%s created  TXT   %s.", stem, outf)
        return os.path.isfile(outf)

    def create_pdf(self):
        exe = self.config.linuxdoc_htmldoc
        inf = self.output.name_htmls
        assert os.path.exists(inf)
        outf = self.output.name_pdf
        stem = self.source.stem
        logdir = self.output.logdir
        logger.debug("%s creating PDF   %s.", stem, outf)
        cmd = [exe, '--size', 'universal', '-t', 'pdf', '--firstpage', 'p1',
               '--outfile', outf, inf]
        result = execute(cmd, logdir=logdir)
        if result != 0:
            return False
        logger.info("%s created  PDF   %s.", stem, outf)
        return os.path.isfile(outf)

    def create_html(self):
        exe = self.config.linuxdoc_sgml2html
        inf = self.source.filename
        assert os.path.exists(inf)
        outf = self.output.name_html
        stem = self.source.stem
        logdir = self.output.logdir
        logger.debug("%s creating HTML  %s, etc.", stem, outf)
        cmd = [exe, inf]
        result = execute(cmd, logdir=logdir)
        if result == 0:  # -- only symlink, if HTML generated successfully
            logger.info("%s created  HTML  %s, etc.", stem, outf)
            target = os.path.basename(outf)
            logger.debug("%s creating index.html symlink to %s.", stem, target)
            try:
                os.symlink(target, 'index.html')
            except OSError:
                logger.debug("%s failed in creating index.html symlink.", stem)
        return os.path.isfile(outf)

    def create_htmls(self):
        exe = self.config.linuxdoc_sgml2html
        inf = self.source.filename
        assert os.path.exists(inf)
        outf = self.output.name_htmls
        stem = self.source.stem
        logdir = self.output.logdir
        logger.debug("%s creating HTMLS %s.", stem, outf)
        cmd = [exe, '--split=0', inf]
        result = execute(cmd, logdir=logdir)
        if result == 0:  # -- only rename, if HTML generated successfully
            logger.info("%s created  HTMLS %s.", stem, outf)
            source = os.path.basename(self.output.name_html)
            target = os.path.basename(self.output.name_htmls)
            logger.debug("%s renaming HTMLS to %s.", stem, target)
            try:
                os.rename(source, target)
            except OSError:
                logger.debug("%s failed renaming HTML single file to %s.",
                             stem, target)
        return os.path.isfile(outf)

#
# -- end of file
