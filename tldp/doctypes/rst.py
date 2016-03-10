#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from tldp.doctypes.common import BaseDoctype

logger = logging.getLogger(__name__)


class RestructuredText(BaseDoctype):
    formatname = 'reStructuredText'
    extensions = ['.rst']
    signatures = []


#
# -- end of file
