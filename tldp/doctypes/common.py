#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import sys
import stat
import time
import errno
import codecs
import shutil
import logging
import inspect
from tempfile import NamedTemporaryFile as ntf
from functools import wraps
import networkx as nx

from tldp.utils import execute, logtimings, writemd5sums

logger = logging.getLogger(__name__)

preamble = '''#! /bin/bash
set -x
set -e
set -o pipefail
'''

postamble = '''
# -- end of file'''


def depends(*predecessors):
    '''decorator to be used for constructing build order graph'''
    def anon(f):
        @wraps(f)
        def method(self, *args, **kwargs):
            return f(self, *args, **kwargs)
        method.depends = [x.__name__ for x in predecessors]
        return method
    return anon


class SignatureChecker(object):

    @classmethod
    def signatureLocation(cls, buf, fname):
        for sig in cls.signatures:
            try:
                sindex = buf.index(sig)
                logger.debug("YES FOUND signature %r in %s at %s; doctype %s.",
                             sig, fname, sindex, cls)
                return sindex
            except ValueError:
                logger.debug("not found signature %r in %s for type %s",
                             sig, fname, cls.__name__)
        return None


class BaseDoctype(object):

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.source.stem,)

    def __init__(self, *args, **kwargs):
        self.source = kwargs.get('source', None)
        self.output = kwargs.get('output', None)
        self.config = kwargs.get('config', None)
        self.removals = set()
        assert self.source is not None
        assert self.output is not None
        assert self.config is not None

    def cleanup(self):
        stem = self.source.stem
        removals = getattr(self, 'removals', None)
        if removals:
            for fn in removals:
                logger.debug("%s cleaning up intermediate file %s", stem, fn)
                try:
                    os.unlink(fn)
                except OSError as e:
                    if e.errno is errno.ENOENT:
                        logger.error("%s missing file at cleanup %s", stem, fn)
                    else:
                        raise e

    def build_precheck(self):
        classname = self.__class__.__name__
        if self.config.script:
            return True
        for tool, validator in self.required.items():
            thing = getattr(self.config, tool, None)
            logger.debug("%s, tool = %s, thing = %s", classname, tool, thing)
            if thing is None:
                logger.error("%s missing required tool %s, skipping...",
                             classname, tool)
                return False
            assert validator(thing)
        return True

    def clear_output(self, **kwargs):
        '''remove the entire output directory

        This method must be --script aware.  The method execute_shellscript()
        generates scripts into the directory that would be removed.  Thus, the
        behaviour is different depending on --script mode or --build mode.
        '''
        logger.debug("%s removing dir   %s.",
                     self.output.stem, self.output.dirname)
        if self.config.script:
            s = 'test -d "{output.dirname}" && rm -rf -- "{output.dirname}"'
            return self.shellscript(s, **kwargs)
        if os.path.exists(self.output.dirname):
            shutil.rmtree(self.output.dirname)
        return True

    def mkdir_output(self, **kwargs):
        '''create a new output directory

        This method must be --script aware.  The method execute_shellscript()
        generates scripts into the directory that would be removed.  Thus, the
        behaviour is different depending on --script mode or --build mode.
        '''
        logger.debug("%s creating dir   %s.",
                     self.output.stem, self.output.dirname)
        if self.config.script:
            s = 'mkdir -p -- "{output.logdir}"'
            return self.shellscript(s, **kwargs)
        for d in (self.output.dirname, self.output.logdir):
            if not os.path.isdir(d):
                os.mkdir(d)
        return True

    def chdir_output(self, **kwargs):
        '''chdir to the output directory (or write the script that would)'''
        logger.debug("%s chdir to dir   %s.",
                     self.output.stem, self.output.dirname)
        if self.config.script:
            s = '''
# - - - - - {source.stem} - - - - - -

cd -- "{output.dirname}"'''
            return self.shellscript(s, **kwargs)
        os.chdir(self.output.dirname)
        return True

    def generate_md5sums(self, **kwargs):
        logger.debug("%s generating MD5SUMS in %s.",
                     self.output.stem, self.output.dirname)
        timestr = time.strftime('%F-%T', time.gmtime())
        md5file = self.output.MD5SUMS
        if self.config.script:
            l = list()
            for fname, hashval in sorted(self.source.md5sums.items()):
                l.append('# {}  {}'.format(hashval, fname))
            md5s = '\n'.join(l)
            s = '''# -- MD5SUMS file from source tree at {}
#
# md5sum > {} -- {}
#
{}
#'''
            s = s.format(timestr,
                         md5file,
                         ' '.join(self.source.md5sums.keys()),
                         md5s)
            return self.shellscript(s, **kwargs)
        header = '# -- MD5SUMS for {}'.format(self.source.stem)
        writemd5sums(md5file, self.source.md5sums, header=header)
        return True

    def copy_static_resources(self, **kwargs):
        logger.debug("%s copy resources %s.",
                     self.output.stem, self.output.dirname)
        source = list()
        for d in self.config.resources:
            fullpath = os.path.join(self.source.dirname, d)
            fullpath = os.path.abspath(fullpath)
            if os.path.isdir(fullpath):
                source.append('"' + fullpath + '"')
        if not source:
            logger.debug("%s no images or resources to copy", self.source.stem)
            return True
        s = 'rsync --archive --verbose %s ./' % (' '.join(source))
        return self.shellscript(s, **kwargs)

    def hook_build_success(self):
        stem = self.output.stem
        logdir = self.output.logdir
        dirname = self.output.dirname
        logger.info("%s build SUCCESS  %s.", stem, dirname)
        logger.debug("%s removing logs  %s)", stem, logdir)
        if os.path.isdir(logdir):
            shutil.rmtree(logdir)
        return True

    def hook_build_failure(self):
        pass

    def shellscript(self, script, **kwargs):
        if self.config.build:
            return self.execute_shellscript(script, **kwargs)
        elif self.config.script:
            return self.dump_shellscript(script, **kwargs)
        else:
            etext = '%s in shellscript, neither --build nor --script'
            raise Exception(etext % (self.source.stem,))

    @logtimings(logger.debug)
    def dump_shellscript(self, script, preamble=preamble,
                         postamble=postamble, **kwargs):
        source = self.source
        output = self.output
        config = self.config
        file = kwargs.get('file', sys.stdout)
        s = script.format(output=output, source=source, config=config)
        print('', file=file)
        print(s, file=file)
        return True

    @logtimings(logger.debug)
    def execute_shellscript(self, script, preamble=preamble,
                            postamble=postamble, **kwargs):
        source = self.source
        output = self.output
        config = self.config

        logdir = output.logdir
        prefix = source.doctype.__name__ + '-'

        s = script.format(output=output, source=source, config=config)
        tf = ntf(dir=logdir, prefix=prefix, suffix='.sh', delete=False)
        tf.close()
        with codecs.open(tf.name, 'w', encoding='utf-8') as f:
            if preamble:
                f.write(preamble)
            f.write(s)
            if postamble:
                f.write(postamble)

        mode = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR
        os.chmod(tf.name, mode)

        cmd = [tf.name]
        result = execute(cmd, logdir=logdir)
        if result != 0:
            with codecs.open(tf.name, encoding='utf-8') as f:
                for line in f:
                    logger.info("Script: %s", line.rstrip())
            return False
        return True

    def build_prepare(self, **kwargs):
        stem = self.source.stem
        classname = self.__class__.__name__
        order = ['build_precheck',
                 'clear_output',
                 'mkdir_output',
                 'chdir_output',
                 'generate_md5sums',
                 'copy_static_resources',
                 ]

        for methname in order:
            method = getattr(self, methname, None)
            assert method is not None
            logger.info("%s calling method %s.%s",
                        stem, classname, method.__name__)
            if not method(**kwargs):
                logger.error("%s called method  %s.%s failed, skipping...",
                             stem, classname, method.__name__)
                return False
        return True

    def determinebuildorder(self):
        graph = nx.DiGraph()
        d = dict(inspect.getmembers(self, inspect.ismethod))
        for name, member in d.items():
            predecessors = getattr(member, 'depends', None)
            if predecessors:
                for pred in predecessors:
                    method = d.get(pred, None)
                    assert method is not None
                    graph.add_edge(method, member)
        order = nx.dag.topological_sort(graph)
        return order

    @logtimings(logger.debug)
    def build_fullrun(self, **kwargs):
        stem = self.source.stem
        order = self.determinebuildorder()
        logger.debug("%s build order %r", self.source.stem, order)
        for method in order:
            classname = self.__class__.__name__
            logger.info("%s calling method %s.%s",
                        stem, classname, method.__name__)
            if not method(**kwargs):
                logger.error("%s called method  %s.%s failed, skipping...",
                             stem, classname, method.__name__)
                return False
        return True

    @logtimings(logger.info)
    def generate(self, **kwargs):
        # -- perform build preparation steps;
        #     - check for all executables and data files
        #     - clear output dir
        #     - make output dir
        #     - chdir to output dir
        #     - copy source images/resources to output dir
        #
        if not self.config.script:
            opwd = os.getcwd()
        if not self.build_prepare():
            return False

        # -- build
        #
        result = self.build_fullrun(**kwargs)

        # -- always clean the kitchen
        #
        self.cleanup()

        # -- report on result and/or cleanup
        #
        if result:
            self.hook_build_success()
        else:
            self.hook_build_failure()

        if not self.config.script:
            os.chdir(opwd)

        return result

#
# -- end of file
