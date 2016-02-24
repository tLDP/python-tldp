#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import stat
from tempfile import NamedTemporaryFile as ntf

from tldp.utils import logger, which, execute, firstfoundfile
from tldp.utils import arg_isexecutable, isexecutable
from tldp.utils import arg_isreadablefile, isreadablefile

from tldp.doctypes.common import BaseDoctype, SignatureChecker


def xslchunk_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/html/tldp-sections.xsl',
         ]
    return firstfoundfile(l)


def xslsingle_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/html/tldp-one-page.xsl',
         ]
    return firstfoundfile(l)


def xslprint_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/fo/tldp-print.xsl',
         ]
    return firstfoundfile(l)


def config_fragment(p):
    p.add_argument('--docbook4xml-xslchunk', type=arg_isreadablefile,
                   default=xslchunk_finder(),
                   help='full path to LDP HTML chunker XSL [%(default)s]')
    p.add_argument('--docbook4xml-xslsingle', type=arg_isreadablefile,
                   default=xslsingle_finder(),
                   help='full path to LDP HTML single-page XSL [%(default)s]')
    p.add_argument('--docbook4xml-xslprint', type=arg_isreadablefile,
                   default=xslprint_finder(),
                   help='full path to LDP FO print XSL [%(default)s]')
    p.add_argument('--docbook4xml-xsltproc', type=arg_isexecutable,
                   default=which('xsltproc'),
                   help='full path to xsltproc [%(default)s]')
    p.add_argument('--docbook4xml-html2text', type=arg_isexecutable,
                   default=which('html2text'),
                   help='full path to html2text [%(default)s]')
    p.add_argument('--docbook4xml-fop', type=arg_isexecutable,
                   default=which('fop'),
                   help='full path to fop [%(default)s]')
    p.add_argument('--docbook4xml-dblatex', type=arg_isexecutable,
                   default=which('dblatex'),
                   help='full path to dblatex [%(default)s]')


class Docbook4XML(BaseDoctype, SignatureChecker):
    formatname = 'DocBook XML 4.x'
    extensions = ['.xml']
    signatures = ['-//OASIS//DTD DocBook XML V4.1.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.4//EN',
                  '-//OASIS//DTD DocBook XML V4.5//EN', ]
    required = {'docbook4xml_xsltproc': isexecutable,
                'docbook4xml_html2text': isexecutable,
                'docbook4xml_dblatex': isexecutable,
                'docbook4xml_fop': isexecutable,
                'docbook4xml_xslchunk': isreadablefile,
                'docbook4xml_xslsingle': isreadablefile,
                'docbook4xml_xslprint': isreadablefile,
                }

    buildorder = ['shellscript']
    script = '''#! /bin/bash
#
# -- generate LDP outputs from DocBook XML 4.x

set -x
set -e
set -o pipefail

cd "{output.dirname}"

"{config.docbook4xml_xsltproc}" > "{output.name_htmls}" \\
  --nonet \\
  --stringparam admon.graphics.path images/ \\
  --stringparam base.dir . \\
  "{config.docbook4xml_xslsingle}" \\
  "{source.filename}"

"{config.docbook4xml_html2text}" > "{output.name_txt}" \\
  -style pretty \\
  -nobs \\
  "{output.name_htmls}"

"{config.docbook4xml_xsltproc}" > "{output.name_fo}" \\
  "{config.docbook4xml_xslprint}" \\
  "{source.filename}"

"{config.docbook4xml_fop}" \\
  -fo "{output.name_fo}" \\
  -pdf "{output.name_pdf}" \\
  && rm -f -- "{output.name_fo}"

# "{config.docbook4xml_dblatex}" \\
#   -F xml \\
#   -t pdf \\
#   -o "{output.name_pdf}" \\
#      "{source.filename}"

"{config.docbook4xml_xsltproc}" \\
  --nonet \\
  --stringparam admon.graphics.path images/ \\
  --stringparam base.dir . \\
  "{config.docbook4xml_xslchunk}" \\
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

    def shellscript(self):
        source = self.source
        output = self.output
        logdir = self.output.logdir
        config = self.config

        s = self.script.format(output=self.output,
                               source=self.source,
                               config=self.config)
        tf = ntf(dir=self.output.logdir, prefix='docbook4xml-shell-', 
                 suffix='.sh', delete=False)
        tf.write(s)
        tf.close()

        mode = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR
        os.chmod(tf.name, mode)

        cmd = [tf.name]
        result = execute(cmd, logdir=logdir)
        if result != 0:
            return False
        return self.output.iscomplete


#
# -- end of file
