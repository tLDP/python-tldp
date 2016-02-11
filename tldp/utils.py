#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import sys
import logging


def getLogger(**opts):
    level = opts.get('level', logging.INFO)
    logging.basicConfig(stream=sys.stderr, level=level)
    logger = logging.getLogger()
    return logger

logger = getLogger()


def runner(cmd, env, stdin, stdout, stderr):
    pass

#
# -- end of file
