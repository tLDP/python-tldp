#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import stat
import logging
from tempfile import NamedTemporaryFile as ntf
from functools import wraps
import networkx as nx

from tldp.utils import execute

logger = logging.getLogger(__name__)

preamble = '''#! /bin/bash
set -x
set -e
set -o pipefail

'''

def depends(graph, *predecessors):
    '''decorator to be used for constructing build order graph'''
    def anon(f):
        for dep in predecessors:
            graph.add_edge(dep.__name__, f.__name__)

        @wraps(f)
        def method(self, *args, **kwargs):
            return f(self, *args, **kwargs)
        return method
    return anon


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

    def shellscript(self, script, preamble=preamble):
        source = self.source
        output = self.output
        config = self.config

        logdir = output.logdir
        prefix = source.doctype.__name__ + '-'

        s = script.format(output=output, source=source, config=config)
        tf = ntf(dir=logdir, prefix=prefix, suffix='.sh', delete=False)
        if preamble:
            tf.write(preamble)
        tf.write(s)
        tf.close()

        mode = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR
        os.chmod(tf.name, mode)

        cmd = [tf.name]
        result = execute(cmd, logdir=logdir)
        if result != 0:
            return False
        return True

    def buildall(self):
        stem = self.source.stem
        order = nx.dag.topological_sort(self.graph)
        logger.debug("%s build order %r", self.source.stem, order)
        for dep in order:
            method = getattr(self, dep, None)
            assert method is not None
            logger.info("%s calling method %s", stem, dep)
            if not method():
                logger.error("%s reported method %s failure, skipping...",
                             stem, dep)
                return False
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
            logger.warning("%s %s failed (%s), skipping to next build",
                           'build_precheck', self.source.stem,
                           self.source.doctype.formatname)
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
                    logger.warning("%s pre_%s failed, skipping to next build",
                                   self.source.stem, target)
                    break

            vector.append(mainmethod())
            if not last_command():
                logger.warning("%s %s failed, skipping to next build",
                               self.source.stem, target)
                break

            if postmethod:
                vector.append(postmethod())
                if not last_command():
                    logger.warning("%s post_%s failed, skipping to next build",
                                   self.source.stem, target)
                    break

        result = all(vector)
        if result:
            self.output.hook_build_success()
        else:
            self.output.hook_build_failure()
        os.chdir(opwd)
        return result

#
# -- end of file
