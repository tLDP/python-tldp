#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import logging
logger = logging.getLogger()

from tldp.utils import which, execute, firstfoundfile
from tldp.utils import arg_isexecutable, isexecutable
from tldp.utils import arg_isreadablefile, isreadablefile

from tldp.doctypes.common import BaseDoctype, SignatureChecker


def docbookdsl_finder():
    locations = [
      '/usr/share/sgml/docbook/stylesheet/dsssl/modular/html/docbook.dsl',
      '/usr/share/sgml/docbook/dsssl-stylesheets/html/docbook.dsl',
      ]
    return firstfoundfile(locations)


def ldpdsl_finder():
    locations = [
      '/usr/share/sgml/docbook/stylesheet/dsssl/ldp/ldp.dsl',
      ]
    return firstfoundfile(locations)


class DocbookSGML(BaseDoctype, SignatureChecker):
    formatname = 'DocBook SGML 3.x/4.x'
    extensions = ['.sgml']
    signatures = ['-//Davenport//DTD DocBook V3.0//EN',
                  '-//OASIS//DTD DocBook V3.1//EN',
                  '-//OASIS//DTD DocBook V4.1//EN',
                  '-//OASIS//DTD DocBook V4.2//EN', ]

    required = {'docbooksgml_jw': isexecutable,
                'docbooksgml_openjade': isexecutable,
                'docbooksgml_dblatex': isexecutable,
                'docbooksgml_html2text': isexecutable,
                'docbooksgml_collateindex': isexecutable,
                'docbooksgml_ldpdsl': isreadablefile,
                'docbooksgml_docbookdsl': isreadablefile,
                }

    buildorder = ['buildindex', 'buildall']

    indexscript = '''#! /bin/bash
#
# -- generate usable index.sgml from DocBook SGML 3.x/4.x

set -x
set -e
set -o pipefail

cd "{output.dirname}"

"{config.docbooksgml_collateindex}" \\
  -N \\
  -o \\
  "{source.dirname}/index.sgml"

"{config.docbooksgml_openjade}" \\
           -t sgml \\
           -V html-index \\
           -d "{config.docbooksgml_docbookdsl}" \\
           "{source.filename}"

"{config.docbooksgml_collateindex}" \\
  -g \\
  -t Index \\
  -i doc-index \\
  -o "index.sgml" \\
     "HTML.index" \\
     "{source.filename}"

mv \\
  --no-clobber \\
  --verbose \\
  -- "index.sgml" "{source.dirname}/index.sgml"

find . -mindepth 1 -maxdepth 1 -type f -print0 \
  | xargs --null --no-run-if-empty -- rm -f --

# -- end of file'''

    mainscript = '''#! /bin/bash
#
# -- generate LDP outputs from DocBook SGML 3.x/4.x

set -x
set -e
set -o pipefail

cd "{output.dirname}"

"{config.docbooksgml_jw}" \\
  -f docbook \\
  -b html \\
  --dsl "{config.docbooksgml_ldpdsl}#html" \\
  -V nochunks \\
  -V '%callout-graphics-path%=images/callouts/' \\
  -V '%stock-graphics-extension%=.png' \\
  --output . \\
  "{source.filename}"

mv \\
  --no-clobber \\
  --verbose \\
  -- "{output.name_html}" "{output.name_htmls}"

"{config.docbooksgml_html2text}" > "{output.name_txt}" \\
  -style pretty \\
  -nobs \\
  "{output.name_htmls}"

"{config.docbooksgml_jw}" \\
  -f docbook \\
  -b pdf \\
  --output . \\
  "{source.filename}" \\
  || "{config.docbooksgml_dblatex}" \\
      -F sgml \\
      -t pdf \\
      -o "{output.name_pdf}" \\
         "{source.filename}"

"{config.docbooksgml_jw}" \\
  -f docbook \\
  -b html \\
  --dsl "{config.docbooksgml_ldpdsl}#html" \\
  -V '%callout-graphics-path%=images/callouts/' \\
  -V '%stock-graphics-extension%=.png' \\
  --output . \\
  "{source.filename}"

mv \\
  --no-clobber \\
  --verbose \\
  -- "{output.name_indexhtml}" "{output.name_html}"

ln \\
  --symbolic \\
  --relative \\
  --verbose \\
  -- "{output.name_html}" "{output.name_indexhtml}"


# -- end of file'''

    def buildindex(self):
        indexsgml = os.path.join(self.source.dirname, 'index.sgml')
        if os.path.isfile(indexsgml):
            self.indexsgml = lambda: None
            return True

        def unlink_indexsgml():
            os.unlink(indexsgml)

        self.indexsgml = unlink_indexsgml
        return self.shellscript(self.indexscript)

    def buildall(self):
        return self.shellscript(self.mainscript)

    def post_buildall(self):
        self.indexsgml()
        return True

    @staticmethod
    def argparse(p):
        p.add_argument('--docbooksgml-docbookdsl', type=arg_isreadablefile,
                       default=docbookdsl_finder(),
                       help='full path to html/docbook.dsl [%(default)s]')
        p.add_argument('--docbooksgml-ldpdsl', type=arg_isreadablefile,
                       default=ldpdsl_finder(),
                       help='full path to ldp/ldp.dsl [%(default)s]')
        p.add_argument('--docbooksgml-jw', type=arg_isexecutable,
                       default=which('jw'),
                       help='full path to jw [%(default)s]')
        p.add_argument('--docbooksgml-html2text', type=arg_isexecutable,
                       default=which('html2text'),
                       help='full path to html2text [%(default)s]')
        p.add_argument('--docbooksgml-openjade', type=arg_isexecutable,
                       default=which('openjade'),
                       help='full path to openjade [%(default)s]')
        p.add_argument('--docbooksgml-dblatex', type=arg_isexecutable,
                       default=which('dblatex'),
                       help='full path to dblatex [%(default)s]')
        p.add_argument('--docbooksgml-collateindex', type=arg_isexecutable,
                       default=which('collateindex'),
                       help='full path to collateindex [%(default)s]')



#
# -- end of file
