#! /usr/bin/python

from ..utils import logger
from .common import SignatureChecker


class Linuxdoc(SignatureChecker):
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]

    def create_txt(self):
        pass

    def create_pdf(self):
        pass

    def create_html(self):
        pass

    def create_htmls(self):
        pass

#
# -- end of file
