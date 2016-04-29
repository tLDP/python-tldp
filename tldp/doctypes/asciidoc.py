#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import logging

from tldp.utils import which
from tldp.utils import arg_isexecutable, isexecutable
from tldp.doctypes.common import depends
from tldp.doctypes.docbook4xml import Docbook4XML

logger = logging.getLogger(__name__)


class Asciidoc(Docbook4XML):
    formatname = 'AsciiDoc'
    extensions = ['.txt']
    signatures = []

    required = {'asciidoc_asciidoc': isexecutable,
                'asciidoc_xmllint': isexecutable,
                }
    required.update(Docbook4XML.required)

    def make_docbook45(self, **kwargs):
        s = '''"{config.asciidoc_asciidoc}" \\
                 --backend docbook45 \\
                 --out-file {output.validsource} \\
                 "{source.filename}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_docbook45)
    def make_validated_source(self, **kwargs):
        s = '"{config.asciidoc_xmllint}" --noout --valid "{output.validsource}"'
        return self.shellscript(s, **kwargs)

    @classmethod
    def argparse(cls, p):
        descrip = 'executables and data files for %s' % (cls.formatname,)
        g = p.add_argument_group(title=cls.__name__, description=descrip)
        g.add_argument('--asciidoc-asciidoc', type=arg_isexecutable,
                       default=which('asciidoc'),
                       help='full path to asciidoc [%(default)s]')
        g.add_argument('--asciidoc-xmllint', type=arg_isexecutable,
                       default=which('xmllint'),
                       help='full path to xmllint [%(default)s]')

#
# -- end of file
