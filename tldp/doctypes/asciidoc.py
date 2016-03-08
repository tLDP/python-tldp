#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from tldp.utils import which
from tldp.utils import arg_isexecutable, isexecutable
from tldp.doctypes.common import BaseDoctype, depends

logger = logging.getLogger(__name__)


class Asciidoc(BaseDoctype):
    formatname = 'AsciiDoc'
    extensions = ['.txt']
    signatures = []

    required = {'asciidoc_a2x': isexecutable,
                }

    def make_docbook45(self):
        s = '''"{config.asciidoc_asciidoc}" \\
                 --backend docbook45 \\
                 --out-file {output.validsource} \\
                 "{source.filename}"'''
        return self.shellscript(s)

    @depends(make_docbook45)
    def docbook_subbuild(self):
        config = self.config
        source = self.output.validsource
        return True


    @classmethod
    def argparse(cls, p):
        descrip = 'executables and data files for %s' % (cls.formatname,)
        g = p.add_argument_group(title=cls.__name__, description=descrip)
        g.add_argument('--asciidoc-asciidoc', type=arg_isexecutable,
                       default=which('asciidoc'),
                       help='full path to asciidoc [%(default)s]')

#
# -- end of file
