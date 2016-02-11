#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import string
from ..utils import logger


class SignatureChecker(object):

    @classmethod
    def signatureLocation(cls, name, fin):
        fin.seek(0)
        buf = fin.read(1024)
        for sig in cls.signatures:
            try:
                sindex = string.index(buf.lower(), sig.lower())
                logger.debug("In file %s, signature %s found at %s; doctype %s found",
                             name, sig, sindex, cls)
                return sindex
            except ValueError:
                logger.debug("In file %s, signature %s not found for document type %s",
                             name, sig, cls.__name__)
        return None

#
# -- end of file
