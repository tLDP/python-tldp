
from __future__ import absolute_import, division, print_function

import os

try:
    from types import SimpleNamespace
except ImportError:
    from utils import SimpleNamespace

import tldp.doctypes

opj = os.path.join
opd = os.path.dirname
opa = os.path.abspath
sampledocs = opa(opj(opd(__file__), 'sample-documents'))

ex_linuxdoc = SimpleNamespace(
               ext='.sgml',
               type=tldp.doctypes.linuxdoc.Linuxdoc,
               filename=opj(sampledocs, 'linuxdoc-simple.sgml'),
              )

ex_docbooksgml = SimpleNamespace(
                  ext='.sgml',
                  type=tldp.doctypes.docbooksgml.DocbookSGML,
                  filename=opj(sampledocs, 'docbooksgml-simple.sgml'),
                 )

ex_docbook4xml = SimpleNamespace(
                 ext='.xml',
                 type=tldp.doctypes.docbook4xml.Docbook4XML,
                 filename=opj(sampledocs, 'docbook4xml-simple.xml'),
                )

ex_docbook5xml = SimpleNamespace(
                 ext='.xml',
                 type=tldp.doctypes.docbook5xml.Docbook5XML,
                 filename=opj(sampledocs, 'docbook5xml-simple.xml'),
                )

ex_rst = SimpleNamespace(
          ext='.rst',
          type=tldp.doctypes.rst.RestructuredText,
          filename=opj(sampledocs, 'restructuredtext-simple.rst'),
         )

ex_text = SimpleNamespace(
           ext='.txt',
           type=tldp.doctypes.text.Text,
           filename=opj(sampledocs, 'text-simple.txt'),
          )

ex_markdown = SimpleNamespace(
               ext='.md',
               type=tldp.doctypes.markdown.Markdown,
               filename=opj(sampledocs, 'markdown-simple.md'),
              )


# -- a bit ugly, but grab each dict
sources = [y for x, y in locals().items() if x.startswith('ex_')]

for ex in sources:
    ex.content = open(ex.filename).read()


# -- end of file
