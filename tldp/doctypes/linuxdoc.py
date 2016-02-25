#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os

from tldp.utils import logger, which, execute
from tldp.utils import arg_isexecutable, isexecutable
from tldp.doctypes.common import BaseDoctype, SignatureChecker


class Linuxdoc(BaseDoctype, SignatureChecker):
    formatname = 'Linuxdoc'
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]

    required = {'linuxdoc_sgml2html': isexecutable,
                'linuxdoc_html2text': isexecutable,
                'linuxdoc_htmldoc': isexecutable,
                }

    buildorder = ['buildall']
    buildscript = '''#! /bin/bash
#
# -- generate LDP outputs from DocBook XML 4.x

set -x
set -e
set -o pipefail

cd "{output.dirname}"

# -- implicitly creates {output.name_html}
"{config.linuxdoc_sgml2html}" \\
  --split=0 \\
  "{source.filename}"

# -- .... so, it must be rename to {output.name_htmls}
mv \\
  --no-clobber \\
  --verbose \\
  -- "{output.name_html}" "{output.name_htmls}"

"{config.linuxdoc_html2text}" > "{output.name_txt}" \\
  -style pretty \\
  -nobs \\
  "{output.name_htmls}"

"{config.linuxdoc_htmldoc}" \\
  --size universal \\
  -t pdf \\
  --firstpage p1 \\
  --outfile "{output.name_pdf}" \\
  "{output.name_htmls}"

# -- implicitly creates {output.name_html}
"{config.linuxdoc_sgml2html}" \\
  "{source.filename}"

ln \
  --symbolic \
  --relative \
  --verbose \
  -- "{output.name_html}" "{output.name_indexhtml}"

# -- end of file'''

    def buildall(self):
        return self.shellscript(self.buildscript)

    @staticmethod
    def argparse(p):
        p.add_argument('--linuxdoc-sgml2html', type=arg_isexecutable,
                       default=which('sgml2html'),
                       help='full path to sgml2html [%(default)s]')
        p.add_argument('--linuxdoc-html2text', type=arg_isexecutable,
                       default=which('html2text'),
                       help='full path to html2text [%(default)s]')
        p.add_argument('--linuxdoc-htmldoc', type=arg_isexecutable,
                       default=which('htmldoc'),
                       help='full path to htmldoc [%(default)s]')



#
# -- end of file
