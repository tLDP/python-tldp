#! /usr/bin/python
# -*- coding: utf8 -*-

from ..utils import logger, which
from .common import SignatureChecker


def uniconf(p):
    parser.add_argument('--docbooksgml-jw', type=which,
                        help='fully qualified path to jw')
    parser.add_argument('--docbooksgml-html2text', type=which,
                        help='fully qualified path to html2text')
    parser.add_argument('--docbooksgml-openjade', type=which,
                        help='fully qualified path to openjade')
    parser.add_argument('--docbooksgml-dblatex', type=which,
                        help='fully qualified path to dblatex')
    parser.add_argument('--docbooksgml-collateindex', type=which,
                        help='fully qualified path to collateindex')


class DocbookSGML(SignatureChecker):
    formatname = 'DocBook SGML 3.x/4.x'
    extensions = ['.sgml']
    signatures = ['-//Davenport//DTD DocBook V3.0//EN',
                  '-//OASIS//DTD DocBook V3.1//EN',
                  '-//OASIS//DTD DocBook V4.1//EN',
                  '-//OASIS//DTD DocBook V4.2//EN', ]
    tools = ['jw', 'openjade', 'collateindex.pl', 'html2text', 'dblatex']

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
