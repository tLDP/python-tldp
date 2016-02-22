#! /usr/bin/python
# -*- coding: utf8 -*-

import os

from ..utils import logger, which, firstfoundfile
from .common import SignatureChecker


def docbookdsl_finder():
    locations = [
      '/usr/share/sgml/docbook/stylesheet/dsssl/ldp/ldp.dsl',
      '/usr/share/sgml/docbook/dsssl-stylesheets/html/docbook.dsl']
    return firstfoundfile(locations)


def ldpdsl_finder():
    locations = [
      '/usr/share/sgml/docbook/stylesheet/dsssl/modular/html/docbook.dsl']
    return firstfoundfile(locations)


def config_fragment(p):
    p.add_argument('--docbooksgml-docbookdsl', type=str,
                   default=docbookdsl_finder(),
                   help='full path to html/docbook.dsl')
    p.add_argument('--docbooksgml-ldpdsl', type=str,
                   default=ldpdsl_finder(),
                   help='full path to ldp/ldp.dsl')
    p.add_argument('--docbooksgml-jw', type=which,
                   default=which('jw'),
                   help='fully qualified path to executable jw')
    p.add_argument('--docbooksgml-html2text', type=which,
                   default=which('html2text'),
                   help='fully qualified path to executable html2text')
    p.add_argument('--docbooksgml-openjade', type=which,
                   default=which('openjade'),
                   help='fully qualified path to executable openjade')
    p.add_argument('--docbooksgml-dblatex', type=which,
                   default=which('dblatex'),
                   help='fully qualified path to executable dblatex')
    p.add_argument('--docbooksgml-collateindex', type=which,
                   default=which('collateindex'),
                   help='fully qualified path to executable collateindex')


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
