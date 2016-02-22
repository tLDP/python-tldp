#! /usr/bin/python
# -*- coding: utf8 -*-

from ..utils import logger, which
from .common import SignatureChecker


def uniconf(p):
    parser.add_argument('--docbook5xml-xsltproc', type=which,
                        help='fully qualified path to xsltproc')
    parser.add_argument('--docbook5xml-html2text', type=which,
                        help='fully qualified path to html2text')
    parser.add_argument('--docbook5xml-fop', type=which,
                        help='fully qualified path to fop')
    parser.add_argument('--docbook5xml-dblatex', type=which,
                        help='fully qualified path to dblatex')


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
