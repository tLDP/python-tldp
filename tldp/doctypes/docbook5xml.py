#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging
logger = logging.getLogger(__name__)

from tldp.utils import which
from tldp.doctypes.common import BaseDoctype, SignatureChecker


class Docbook5XML(BaseDoctype, SignatureChecker):
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

    @staticmethod
    def argparse(p):
        p.add_argument('--docbook5xml-xsltproc', type=which,
                       default=which('xsltproc'),
                       help='full path to xsltproc [%(default)s]')
        p.add_argument('--docbook5xml-html2text', type=which,
                       default=which('html2text'),
                       help='full path to html2text [%(default)s]')
        p.add_argument('--docbook5xml-fop', type=which,
                       default=which('fop'),
                       help='full path to fop [%(default)s]')
        p.add_argument('--docbook5xml-dblatex', type=which,
                       default=which('dblatex'),
                       help='full path to dblatex [%(default)s]')


#
# -- end of file
