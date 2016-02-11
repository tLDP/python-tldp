#! /usr/bin/python

from ..utils import logger
from .common import SignatureChecker


class DocbookSGML(SignatureChecker):
    extensions = ['.sgml']
    signatures = ['-//Davenport//DTD DocBook V3.0//EN',
                  '-//OASIS//DTD DocBook V3.1//EN',
                  '-//OASIS//DTD DocBook V4.1//EN',
                  '-//OASIS//DTD DocBook V4.2//EN', ]

#
# -- end of file
