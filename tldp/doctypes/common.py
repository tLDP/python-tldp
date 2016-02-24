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

    def build_precheck(self):
        try:
            self.required.items()
        except AttributeError:
            return False

        for tool, validator in self.required.items():
            thing = getattr(self.config, tool, None)
            assert thing is not None
            assert validator(thing)
        return True

    def generate(self):
        # -- the output directory gets to prepare; must return True
        #
        if not self.output.hook_prebuild():
            return False

        opwd = os.getcwd()
        os.chdir(self.output.dirname)

        # -- the processor gets to prepare; must return True
        #
        if not self.build_precheck():
            logger.warning("%s build_precheck failed (%s), skipping to next build", 
                           self.source.stem, self.source.doctype.formatname)
            return False

        # -- now, we can walk through build targets, and record a vector
        #    of success or failure
        #
        vector = list()

        def last_command():
            return vector[-1]

        for target in self.buildorder:
            premethod = getattr(self, 'pre_' + target, None)
            mainmethod = getattr(self, target, None)
            postmethod = getattr(self, 'post_' + target, None)
            assert mainmethod is not None

            if premethod:
                vector.append(premethod())
                if not last_command():
                    logger.warning("%s pre_%s failed, skipping to next target",
                                   self.source.stem, target)
                    continue

            vector.append(mainmethod())
            if not last_command():
                logger.warning("%s %s failed, skipping to next target",
                               self.source.stem, target)
                continue

            if postmethod:
                vector.append(postmethod())
                if not last_command():
                    logger.warning("%s post_%s failed, skipping to next target",
                                   self.source.stem, target)
                    continue

        result = all(vector)
        if result:
            self.output.hook_build_success()
        else:
            self.output.hook_build_failure()
        os.chdir(opwd)
        return result

#
# -- end of file
