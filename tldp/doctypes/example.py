#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from tldp.doctypes.common import BaseDoctype

logger = logging.getLogger(__name__)


class Frobnitz(BaseDoctype):
    formatname = 'Frobnitz'
    extensions = ['.fb']
    signatures = ['{{Frobnitz-Format 2.3}}']

#
# -- end of file
