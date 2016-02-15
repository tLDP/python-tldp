#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
import io
import sys
import subprocess
from tempfile import mkstemp
import logging


def getLogger(**opts):
    level = opts.get('level', logging.DEBUG)
    logging.basicConfig(stream=sys.stderr, level=level)
    logger = logging.getLogger()
    return logger

logger = getLogger()


def execute(cmd, stdin=None, stdout=None, stderr=None,
            logdir=None, env=os.environ):
    prefix = os.path.basename(cmd[0]) + '.' + str(os.getpid()) + '-'

    if logdir is None:
        raise Exception("Missing, required parameter: logdir.")
    assert os.path.isdir(logdir)

    # -- not remapping STDIN, because that doesn't make sense here
    if stdout is None:
        stdout, stdoutname = mkstemp(prefix=prefix, suffix='.stdout',
                                     dir=logdir)
    if stderr is None:
        stderr, stderrname = mkstemp(prefix=prefix, suffix='.stderr',
                                     dir=logdir)

    logger.debug("About to execute: %r", cmd)
    proc = subprocess.Popen(cmd, shell=False, close_fds=True,
                            stdin=stdin, stdout=stdout, stderr=stderr,
                            env=env, preexec_fn=os.setsid)
    result = proc.wait()
    if result != 0:
        logger.warning("Return code (%s) for process: %r", result, cmd)
        logger.warning("Find STDOUT/STDERR in %s/%s", logdir, prefix)
    return result


def is_executable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    '''return None or the full path to an executable (respecting $PATH)
http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    '''
    fpath, fname = os.path.split(program)
    if fpath and is_executable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            sut = os.path.join(path, program)
            if is_executable(sut):
                return sut
    return None


def makefh(thing):
    if isinstance(thing, io.IOBase):
        f = thing
    elif isinstance(thing, str) and os.path.isfile(thing):
        f = open(thing)
    else:
        raise TypeError("Cannot make file from %s of %r" %
                        (type(thing), thing,))
    return f

#
# -- end of file
