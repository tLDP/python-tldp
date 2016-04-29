
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import codecs
from argparse import Namespace

import tldp.doctypes

from tldptesttools import stem_and_ext

opj = os.path.join
opd = os.path.dirname
opa = os.path.abspath
sampledocs = opa(opj(opd(__file__), 'sample-documents'))


def load_content(ex):
    with codecs.open(ex.filename, encoding='utf-8') as f:
        ex.content = f.read()
    ex.stem, ex.ext = stem_and_ext(ex.filename)


ex_linuxdoc = Namespace(
    doctype=tldp.doctypes.linuxdoc.Linuxdoc,
    filename=opj(sampledocs, 'linuxdoc-simple.sgml'),)

ex_docbooksgml = Namespace(
    doctype=tldp.doctypes.docbooksgml.DocbookSGML,
    filename=opj(sampledocs, 'docbooksgml-simple.sgml'),)

ex_docbook4xml = Namespace(
    doctype=tldp.doctypes.docbook4xml.Docbook4XML,
    filename=opj(sampledocs, 'docbook4xml-simple.xml'),)

ex_docbook5xml = Namespace(
    doctype=tldp.doctypes.docbook5xml.Docbook5XML,
    filename=opj(sampledocs, 'docbook5xml-simple.xml'),)

ex_asciidoc = Namespace(
    doctype=tldp.doctypes.asciidoc.Asciidoc,
    filename=opj(sampledocs, 'asciidoc-complete.txt'),)

ex_linuxdoc_dir = Namespace(
    doctype=tldp.doctypes.linuxdoc.Linuxdoc,
    filename=opj(sampledocs, 'Linuxdoc-Larger',
                             'Linuxdoc-Larger.sgml'),)

ex_docbook4xml_dir = Namespace(
    doctype=tldp.doctypes.docbook4xml.Docbook4XML,
    filename=opj(sampledocs, 'DocBook-4.2-WHYNOT',
                             'DocBook-4.2-WHYNOT.xml'),)

ex_docbooksgml_dir = Namespace(
    doctype=tldp.doctypes.docbooksgml.DocbookSGML,
    filename=opj(sampledocs, 'DocBookSGML-Larger',
                             'DocBookSGML-Larger.sgml'),)

# -- a bit ugly, but grab each dict
sources = [y for x, y in locals().items() if x.startswith('ex_')]

for ex in sources:
    load_content(ex)

unknown_doctype = Namespace(
    doctype=None,
    filename=opj(sampledocs, 'Unknown-Doctype.xqf'),)

broken_docbook4xml = Namespace(
    doctype=tldp.doctypes.docbook4xml.Docbook4XML,
    filename=opj(sampledocs, 'docbook4xml-broken.xml'),)

load_content(broken_docbook4xml)

# -- end of file
