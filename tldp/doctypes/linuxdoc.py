#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import logging
import networkx as nx

from tldp.utils import which
from tldp.utils import arg_isexecutable, isexecutable
from tldp.doctypes.common import BaseDoctype, SignatureChecker, depends

logger = logging.getLogger(__name__)


class Linuxdoc(BaseDoctype, SignatureChecker):
    formatname = 'Linuxdoc'
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]

    required = {'linuxdoc_sgml2html': isexecutable,
                'linuxdoc_html2text': isexecutable,
                'linuxdoc_htmldoc': isexecutable,
                }

    graph = nx.DiGraph()

    buildorder = ['buildall']

    def chdir_output(self):
        os.chdir(self.output.dirname)
        return True

    @depends(graph, chdir_output)
    def make_htmls(self):
        '''create a single page HTML output (with incorrect name)'''
        s = '"{config.linuxdoc_sgml2html}" --split=0 "{source.filename}"'
        return self.shellscript(s)

    @depends(graph, make_htmls)
    def make_name_htmls(self):
        '''correct the single page HTML output name'''
        s = 'mv -v --no-clobber -- "{output.name_html}" "{output.name_htmls}"'
        return self.shellscript(s)

    @depends(graph, make_name_htmls)
    def make_name_txt(self):
        '''create text output (from single-page HTML)'''
        s = '''"{config.linuxdoc_html2text}" > "{output.name_txt}" \\
                  -style pretty \\
                  -nobs \\
                  "{output.name_htmls}"'''
        return self.shellscript(s)

    @depends(graph, make_name_htmls)
    def make_name_pdf(self):
        s = '''"{config.linuxdoc_htmldoc}" \\
                 --size universal \\
                 -t pdf \\
                 --firstpage p1 \\
                 --outfile "{output.name_pdf}" \\
                 "{output.name_htmls}"'''
        return self.shellscript(s)

    @depends(graph, make_name_htmls)
    def make_name_html(self):
        '''create final index.html symlink'''
        s = '"{config.linuxdoc_sgml2html}" "{source.filename}"'
        return self.shellscript(s)

    @depends(graph, make_name_html)
    def make_name_indexhtml(self):
        '''create final index.html symlink'''
        s = 'ln -svr -- "{output.name_html}" "{output.name_indexhtml}"'
        return self.shellscript(s)

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
