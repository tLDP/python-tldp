#! /usr/bin/python
# -*- coding: utf8 -*-

from ..utils import logger, which
from .common import SignatureChecker


def uniconf(p):
    parser.add_argument('--docbook4xml-xsltproc', type=which,
                        help='fully qualified path to xsltproc')
    parser.add_argument('--docbook4xml-html2text', type=which,
                        help='fully qualified path to html2text')
    parser.add_argument('--docbook4xml-fop', type=which,
                        help='fully qualified path to fop')
    parser.add_argument('--docbook4xml-dblatex', type=which,
                        help='fully qualified path to dblatex')


class Docbook4XML(SignatureChecker):
    formatname = 'DocBook XML 4.x'
    extensions = ['.xml']
    signatures = ['-//OASIS//DTD DocBook XML V4.1.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.4//EN',
                  '-//OASIS//DTD DocBook XML V4.5//EN', ]
    tools = ['xsltproc', 'html2text', 'fop', 'dblatex']
    files = ['']

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
