#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import logging

from tldp.utils import which
from tldp.utils import arg_isexecutable, isexecutable
from tldp.doctypes.common import BaseDoctype, SignatureChecker, depends

logger = logging.getLogger(__name__)


class Linuxdoc(BaseDoctype, SignatureChecker):
    formatname = 'Linuxdoc'
    extensions = ['.sgml']
    signatures = ['<!doctype linuxdoc system', ]

    required = {'linuxdoc_sgml2html': isexecutable,
                'linuxdoc_sgmlcheck': isexecutable,
                'linuxdoc_html2text': isexecutable,
                'linuxdoc_htmldoc': isexecutable,
                }

    def validate_source(self, **kwargs):
        s = '"{config.linuxdoc_sgmlcheck}" "{source.filename}"'
        return self.shellscript(s, **kwargs)

    @depends(validate_source)
    def make_htmls(self, **kwargs):
        '''create a single page HTML output (with incorrect name)'''
        s = '"{config.linuxdoc_sgml2html}" --split=0 "{source.filename}"'
        return self.shellscript(s, **kwargs)

    @depends(make_htmls)
    def make_name_htmls(self, **kwargs):
        '''correct the single page HTML output name'''
        s = 'mv -v --no-clobber -- "{output.name_html}" "{output.name_htmls}"'
        return self.shellscript(s, **kwargs)

    @depends(make_name_htmls)
    def make_name_txt(self, **kwargs):
        '''create text output (from single-page HTML)'''
        s = '''"{config.linuxdoc_html2text}" > "{output.name_txt}" \\
                  -style pretty \\
                  -nobs \\
                  "{output.name_htmls}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_name_htmls)
    def make_name_pdf(self, **kwargs):
        s = '''"{config.linuxdoc_htmldoc}" \\
                 --size universal \\
                 --firstpage p1 \\
                 --format pdf \\
                 --footer c.1 \\
                 --outfile "{output.name_pdf}" \\
                 "{output.name_htmls}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_name_htmls)
    def make_name_html(self, **kwargs):
        '''create chunked output'''
        s = '"{config.linuxdoc_sgml2html}" "{source.filename}"'
        return self.shellscript(s, **kwargs)

    @depends(make_name_html)
    def make_name_indexhtml(self, **kwargs):
        '''create final index.html symlink'''
        s = 'ln -svr -- "{output.name_html}" "{output.name_indexhtml}"'
        return self.shellscript(s, **kwargs)

    @classmethod
    def argparse(cls, p):
        descrip = 'executables and data files for %s' % (cls.formatname,)
        g = p.add_argument_group(title=cls.__name__, description=descrip)
        g.add_argument('--linuxdoc-sgmlcheck', type=arg_isexecutable,
                       default=which('sgmlcheck'),
                       help='full path to sgmlcheck [%(default)s]')
        g.add_argument('--linuxdoc-sgml2html', type=arg_isexecutable,
                       default=which('sgml2html'),
                       help='full path to sgml2html [%(default)s]')
        g.add_argument('--linuxdoc-html2text', type=arg_isexecutable,
                       default=which('html2text'),
                       help='full path to html2text [%(default)s]')
        g.add_argument('--linuxdoc-htmldoc', type=arg_isexecutable,
                       default=which('htmldoc'),
                       help='full path to htmldoc [%(default)s]')

#
# -- end of file
