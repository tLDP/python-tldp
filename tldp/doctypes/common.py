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
        self.source = kwargs.get('source', None)
        self.output = kwargs.get('output', None)
        self.platform = kwargs.get('platform', None)
        assert None not in (self.source, self.output, self.platform)

    def generate(self):
        self.output.prebuild_hook()
        os.chdir(self.output.dirname)
        vector = [self.output.clean(),
                  self.platform_check(),
                  self.create_htmls(),
                  self.create_pdf(),
                  self.create_txt(),
                  self.create_html(),
                  ]
        result = all(vector)
        if result:
            self.output.build_success_hook()
        else:
            self.output.build_failure_hook()
        logger.info("%s generation of all documents %s",
                    self.source.stem, result)
        return all(vector)

#
# -- end of file
