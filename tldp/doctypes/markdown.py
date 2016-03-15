#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import logging

from tldp.doctypes.common import BaseDoctype

logger = logging.getLogger(__name__)


class Markdown(BaseDoctype):
    formatname = 'Markdown'
    extensions = ['.md']
    signatures = []
    tools = ['pandoc']

#
# -- end of file
