#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

from .typeguesser import knowndoctypes
from .utils import logger, which


class Platform(object):

    def __init__(self, config):
        for doctype in knowndoctypes:
            for tool in doctype.tools:
                loc = which(tool)
                if loc is None:
                    logger.info("Missing tool %s, needed by %s (%s)",
                                tool, doctype.__name__, doctype.formatname)
                else:
                    setattr(self, tool, loc)


#
# -- end of file
