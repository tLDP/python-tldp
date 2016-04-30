#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import logging

from tldp.doctypes.common import BaseDoctype

logger = logging.getLogger(__name__)


class Frobnitz(BaseDoctype):
    formatname = 'Frobnitz'
    extensions = ['.fb']
    signatures = ['{{Frobnitz-Format 2.3}}']

#
# -- end of file
