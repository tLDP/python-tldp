
from __future__ import absolute_import, division, print_function

import os

import tldp.doctypes

datadir = os.path.join(os.path.dirname(__file__), 'testdata')

ex_linuxdoc = {
               'ext': '.sgml',
               'type': tldp.doctypes.linuxdoc.Linuxdoc,
               'filename': os.path.join(datadir, 'linuxdoc-simple.sgml'),
              }

ex_docbooksgml = {
                  'ext': '.sgml',
                  'type': tldp.doctypes.docbooksgml.DocbookSGML,
                  'filename': os.path.join(datadir, 'docbooksgml-simple.sgml'),
                 }

ex_docbook4xml = {
                 'ext': '.xml',
                 'type': tldp.doctypes.docbook4xml.Docbook4XML,
                 'filename': os.path.join(datadir, 'docbook4xml-simple.xml'),
                }

ex_docbook5xml = {
                 'ext': '.xml',
                 'type': tldp.doctypes.docbook5xml.Docbook5XML,
                 'filename': os.path.join(datadir, 'docbook5xml-simple.xml'),
                }

ex_rst = {
          'ext': '.rst',
          'type': tldp.doctypes.rst.RestructuredText,
          'filename': os.path.join(datadir, 'restructuredtext-simple.rst'),
         }

ex_text = {
           'ext': '.txt',
           'type': tldp.doctypes.text.Text,
           'filename': os.path.join(datadir, 'text-simple.txt'),
          }

ex_markdown = {
               'ext': '.md',
               'type': tldp.doctypes.markdown.Markdown,
               'filename': os.path.join(datadir, 'markdown-simple.md'),
              }


# -- a bit ugly, but grab each dict
examples = [y for x, y in locals().items() if x.startswith('ex_')]

for ex in examples:
    ex['content'] = open(ex['filename']).read()


# -- end of file
