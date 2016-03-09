
from __future__ import absolute_import, division, print_function

import os
from argparse import Namespace

import tldp.doctypes

from tldptesttools import stem_and_ext

opj = os.path.join
opd = os.path.dirname
opa = os.path.abspath
sampledocs = opa(opj(opd(__file__), 'sample-documents'))

ex_linuxdoc = Namespace(
               doctype=tldp.doctypes.linuxdoc.Linuxdoc,
               filename=opj(sampledocs, 'linuxdoc-simple.sgml'),
              )

ex_docbooksgml = Namespace(
                  doctype=tldp.doctypes.docbooksgml.DocbookSGML,
                  filename=opj(sampledocs, 'docbooksgml-simple.sgml'),
                 )

ex_docbook4xml = Namespace(
                 doctype=tldp.doctypes.docbook4xml.Docbook4XML,
                 filename=opj(sampledocs, 'docbook4xml-simple.xml'),
                )

ex_docbook5xml = Namespace(
                 doctype=tldp.doctypes.docbook5xml.Docbook5XML,
                 filename=opj(sampledocs, 'docbook5xml-simple.xml'),
                )

ex_asciidoc = Namespace(
           doctype=tldp.doctypes.asciidoc.Asciidoc,
           filename=opj(sampledocs, 'asciidoc-complete.txt'),
          )
#
# ex_rst = Namespace(
#           doctype=tldp.doctypes.rst.RestructuredText,
#           filename=opj(sampledocs, 'restructuredtext-simple.rst'),
#          )
#
# ex_markdown = Namespace(
#                doctype=tldp.doctypes.markdown.Markdown,
#                filename=opj(sampledocs, 'markdown-simple.md'),
#               )

ex_linuxdoc_dir = Namespace(
               doctype=tldp.doctypes.linuxdoc.Linuxdoc,
               filename=opj(sampledocs, 'Linuxdoc-Larger',
                            'Linuxdoc-Larger.sgml'),
              )

ex_docbook4xml_dir = Namespace(
               doctype=tldp.doctypes.docbook4xml.Docbook4XML,
               filename=opj(sampledocs, 'DocBook-4.2-WHYNOT',
                            'DocBook-4.2-WHYNOT.xml'),
              )

unknown_doctype =  Namespace(
               doctype=None,
               filename=opj(sampledocs, 'Unknown-Doctype.xqf'),
              )

# -- a bit ugly, but grab each dict
sources = [y for x, y in locals().items() if x.startswith('ex_')]

for ex in sources:
    ex.content = open(ex.filename).read()
    ex.stem, ex.ext = stem_and_ext(ex.filename)


# -- end of file
