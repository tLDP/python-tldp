#! /usr/bin/python

import sys
import logging


def getLogger(**opts):
    level = opts.get('level', logging.INFO)
    logging.basicConfig(stream=sys.stderr, level=level)
    logger = logging.getLogger()
    return logger

logger = getLogger()

#
# -- end of file
