#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import string
from ..utils import logger


class SignatureChecker(object):

    @classmethod
    def signatureLocation(cls, f):
        f.seek(0)
        buf = f.read(1024)
        for sig in cls.signatures:
            try:
                sindex = string.index(buf.lower(), sig.lower())
                logger.debug("Found signature %s in %s at %s; doctype %s.",
                             sig, f.name, sindex, cls)
                return sindex
            except ValueError:
                logger.debug("Signature %s not found in %s for type %s",
                             sig, f.name, cls.__name__)
        return None

#
# -- end of file
