#! /usr/bin/python

from ..utils import logger

from .common import SignatureChecker


class Docbook4XML(SignatureChecker):
    extensions = ['.xml']
    signatures = ['-//OASIS//DTD DocBook XML V4.1.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.4//EN',
                  '-//OASIS//DTD DocBook XML V4.5//EN', ]

#
# -- end of file
