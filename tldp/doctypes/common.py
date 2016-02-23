#! /usr/bin/python
# -*- coding: utf8 -*-

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
        self.config = kwargs.get('config', None)
        assert None not in (self.source, self.output, self.config)

    def generate(self):
        def last(l): 
            return l[-1]
        self.output.prebuild_hook()
        os.chdir(self.output.dirname)
        command = list()
        command.append(self.build_precheck())
        if not last(command):
           return False
        command.append(self.create_htmls())
        command.append(self.create_pdf())
        command.append(self.create_txt())
        command.append(self.create_html())

        result = all(command)
        if result:
            self.output.build_success_hook()
        else:
            self.output.build_failure_hook()
        return result

#
# -- end of file
