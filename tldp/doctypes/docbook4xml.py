#! /usr/bin/python
# -*- coding: utf8 -*-

from ..utils import logger, which, firstfoundfile
from .common import SignatureChecker

def xslchunk_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/html/tldp-sections.xsl',
         '/home/mabrown/vcs/LDP/LDP/builder/xsl/ldp-html-chunk.xsl',
         ]
    return firstfoundfile(l)


def xslsingle_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/html/tldp-one-page.xsl',
         '/home/mabrown/vcs/LDP/LDP/builder/xsl/ldp-html.xsl',
         ]
    return firstfoundfile(l)


def xslprint_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/fo/tldp-print.xsl',
         '/home/mabrown/vcs/LDP/LDP/builder/xsl/ldp-print.xsl',
         ]
    return firstfoundfile(l)


def config_fragment(p):
    p.add_argument('--docbook4xml-xslchunk', type=str,
                   default=xslchunk_finder(),
                   help='full path to LDP HTML section chunker XSL')
    p.add_argument('--docbook4xml-xslsingle', type=str,
                   default=xslsingle_finder(),
                   help='full path to LDP HTML single-page XSL')
    p.add_argument('--docbook4xml-xslprint', type=str,
                   default=xslprint_finder(),
                   help='full path to LDP FO print XSL')
    p.add_argument('--docbook4xml-xsltproc', type=which,
                   default=which('xsltproc'),
                   help='fully qualified path to executable xsltproc')
    p.add_argument('--docbook4xml-html2text', type=which,
                   default=which('html2text'),
                   help='fully qualified path to executable html2text')
    p.add_argument('--docbook4xml-fop', type=which,
                   default=which('fop'),
                   help='fully qualified path to executable fop')
    p.add_argument('--docbook4xml-dblatex', type=which,
                   default=which('dblatex'),
                   help='fully qualified path to executable dblatex')


class Docbook4XML(SignatureChecker):
    formatname = 'DocBook XML 4.x'
    extensions = ['.xml']
    signatures = ['-//OASIS//DTD DocBook XML V4.1.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.2//EN',
                  '-//OASIS//DTD DocBook XML V4.4//EN',
                  '-//OASIS//DTD DocBook XML V4.5//EN', ]
    tools = ['xsltproc', 'html2text', 'fop', 'dblatex']
    files = ['']

    def create_txt(self):
        logger.info("Creating txt for %s", self.source.stem)

    def create_pdf(self):
        logger.info("Creating PDF for %s", self.source.stem)

    def create_html(self):
        logger.info("Creating chunked HTML for %s", self.source.stem)

    def create_htmls(self):
        logger.info("Creating single page HTML for %s", self.source.stem)

#
# -- end of file
