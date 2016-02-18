#! /usr/bin/python
# -*- coding: utf8 -*-

from ..utils import logger


class RestructuredText(object):
    formatname = 'reStructuredText'
    extensions = ['.rst']
    signatures = []
    tools = ['rst2html']

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
