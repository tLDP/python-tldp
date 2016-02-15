#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
from ..utils import logger


class SignatureChecker(object):

    @classmethod
    def signatureLocation(cls, f):
        f.seek(0)
        buf = f.read(1024).lower()
        for sig in cls.signatures:
            try:
                sindex = buf.index(sig.lower())
                logger.debug("Found signature %s in %s at %s; doctype %s.",
                             sig, f.name, sindex, cls)
                return sindex
            except ValueError:
                logger.debug("Signature %s not found in %s for type %s",
                             sig, f.name, cls.__name__)
        return None


class BaseDoctype(object):

    def __init__(self, *args, **kwargs):
        self.source = kwargs.get('source')
        self.output = kwargs.get('output')
        self.platform = kwargs.get('platform')
        self.logdir = os.path.join(self.output.dirname, 'logs')
        if os.path.exists(self.logdir):
            logger.warning("Found existing logs directory: %s", self.logdir)
        else:
            os.mkdir(self.logdir)

    def generate(self):
        os.chdir(self.output.dirname)
        self.output.clear()
        self.platform_check()
        self.create_htmls()
        self.create_pdf()
        self.create_txt()
        self.create_html()

#
# -- end of file
