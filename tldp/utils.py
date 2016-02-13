#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import os
import io
import sys
import logging


def getLogger(**opts):
    level = opts.get('level', logging.INFO)
    logging.basicConfig(stream=sys.stderr, level=level)
    logger = logging.getLogger()
    return logger

logger = getLogger()


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
