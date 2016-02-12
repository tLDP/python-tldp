#! /usr/bin/python

from ..utils import logger
from .common import SignatureChecker


class Docbook5XML(SignatureChecker):
    formatname = 'DocBook 5.x XML'
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
