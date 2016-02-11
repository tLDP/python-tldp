#! /usr/bin/python

from ..utils import logger
from .common import SignatureChecker


class Docbook5XML(SignatureChecker):
    extensions = ['.xml']
    signatures = ['-//OASIS//DTD DocBook V5.0/EN',
                  'http://docbook.org/ns/docbook', ]

#
# -- end of file
