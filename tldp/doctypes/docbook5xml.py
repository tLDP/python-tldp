#! /usr/bin/python
# -*- coding: utf8 -*-

from ..utils import logger, which
from .common import SignatureChecker


def config_fragment(p):
    p.add_argument('--docbook5xml-xsltproc', type=which,
                   default=which('xsltproc'),
                   help='fully qualified path to executable xsltproc')
    p.add_argument('--docbook5xml-html2text', type=which,
                   default=which('html2text'),
                   help='fully qualified path to executable html2text')
    p.add_argument('--docbook5xml-fop', type=which,
                   default=which('fop'),
                   help='fully qualified path to executable fop')
    p.add_argument('--docbook5xml-dblatex', type=which,
                   default=which('dblatex'),
                   help='fully qualified path to executable dblatex')


class Docbook5XML(SignatureChecker):
    formatname = 'DocBook XML 5.x'
    extensions = ['.xml']
    signatures = ['-//OASIS//DTD DocBook V5.0/EN',
                  'http://docbook.org/ns/docbook', ]
    tools = ['xsltproc', 'html2text', 'fop', 'dblatex']

    def create_txt(self):
        logger.info("Creating txt for %s", self.source.stem)

    def create_pdf(self):
        logger.info("Creating PDF for %s", self.source.stem)

    def create_html(self):
        logger.info("Creating chunked HTML for %s", self.source.stem)

    def create_htmls(self):
        logger.info("Creating single page HTML for %s", self.source.stem)

#
# -- end of file
