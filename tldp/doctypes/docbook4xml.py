#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import logging

from tldp.utils import which, firstfoundfile
from tldp.utils import arg_isexecutable, isexecutable
from tldp.utils import arg_isreadablefile, isreadablefile
from tldp.utils import arg_isstr, isstr

from tldp.doctypes.common import BaseDoctype, SignatureChecker, depends

logger = logging.getLogger(__name__)


def xslchunk_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/html/tldp-sections.xsl',
         'http://docbook.sourceforge.net/release/xsl/current/html/chunk.xsl',
         ]
    return firstfoundfile(l)


def xslsingle_finder():
    l = ['/usr/share/xml/docbook/stylesheet/ldp/html/tldp-one-page.xsl',
         'http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl',
         ]
    return firstfoundfile(l)


def xslprint_finder():
    l = ['http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl',
         # '/usr/share/xml/docbook/stylesheet/ldp/fo/tldp-print.xsl',
         ]
    return l[0]
    # return firstfoundfile(l)


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
                'docbook4xml_xmllint': isexecutable,
                'docbook4xml_xslchunk': isreadablefile,
                'docbook4xml_xslsingle': isreadablefile,
                'docbook4xml_xslprint': isstr,
                }

    def make_validated_source(self, **kwargs):
        s = '''"{config.docbook4xml_xmllint}" > "{output.validsource}" \\
                  --nonet \\
                  --noent \\
                  --xinclude \\
                  --postvalid \\
                  "{source.filename}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_validated_source)
    def make_name_htmls(self, **kwargs):
        '''create a single page HTML output'''
        s = '''"{config.docbook4xml_xsltproc}" > "{output.name_htmls}" \\
                  --nonet \\
                  --stringparam admon.graphics.path images/ \\
                  --stringparam base.dir . \\
                  "{config.docbook4xml_xslsingle}" \\
                  "{output.validsource}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_name_htmls)
    def make_name_txt(self, **kwargs):
        '''create text output'''
        s = '''"{config.docbook4xml_html2text}" > "{output.name_txt}" \\
                  -style pretty \\
                  -nobs \\
                  "{output.name_htmls}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_validated_source)
    def make_fo(self, **kwargs):
        '''generate the Formatting Objects intermediate output'''
        s = '''"{config.docbook4xml_xsltproc}" > "{output.name_fo}" \\
                  --stringparam fop.extensions 0 \\
                  --stringparam fop1.extensions 1 \\
                  "{config.docbook4xml_xslprint}" \\
                  "{output.validsource}"'''
        if not self.config.script:
            self.removals.add(self.output.name_fo)
        return self.shellscript(s, **kwargs)

    # -- this is conditionally built--see logic in make_name_pdf() below
    # @depends(make_fo)
    def make_pdf_with_fop(self, **kwargs):
        '''use FOP to create a PDF'''
        s = '''"{config.docbook4xml_fop}" \\
                  -fo "{output.name_fo}" \\
                  -pdf "{output.name_pdf}"'''
        return self.shellscript(s, **kwargs)

    # -- this is conditionally built--see logic in make_name_pdf() below
    # @depends(make_validated_source)
    def make_pdf_with_dblatex(self, **kwargs):
        '''use dblatex (fallback) to create a PDF'''
        s = '''"{config.docbook4xml_dblatex}" \\
                  -F xml \\
                  -t pdf \\
                  -o "{output.name_pdf}" \\
                  "{output.validsource}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_validated_source, make_fo)
    def make_name_pdf(self, **kwargs):
        stem = self.source.stem
        classname = self.__class__.__name__
        logger.info("%s calling method %s.%s",
                    stem, classname, 'make_pdf_with_fop')
        if self.make_pdf_with_fop(**kwargs):
            return True
        logger.error("%s %s failed creating PDF, falling back to dblatex...",
                     stem, self.config.docbook4xml_fop)
        logger.info("%s calling method %s.%s",
                    stem, classname, 'make_pdf_with_dblatex')
        return self.make_pdf_with_dblatex(**kwargs)

    @depends(make_validated_source)
    def make_chunked_html(self, **kwargs):
        '''create chunked HTML output'''
        s = '''"{config.docbook4xml_xsltproc}" \\
                  --nonet \\
                  --stringparam admon.graphics.path images/ \\
                  --stringparam base.dir . \\
                  "{config.docbook4xml_xslchunk}" \\
                  "{output.validsource}"'''
        return self.shellscript(s, **kwargs)

    @depends(make_chunked_html)
    def make_name_html(self, **kwargs):
        '''rename DocBook XSL's index.html to LDP standard STEM.html'''
        s = 'mv -v --no-clobber -- "{output.name_indexhtml}" "{output.name_html}"'
        return self.shellscript(s, **kwargs)

    @depends(make_name_html)
    def make_name_indexhtml(self, **kwargs):
        '''create final index.html symlink'''
        s = 'ln -svr -- "{output.name_html}" "{output.name_indexhtml}"'
        return self.shellscript(s, **kwargs)

    @depends(make_name_html, make_name_pdf, make_name_htmls, make_name_txt)
    def remove_validated_source(self, **kwargs):
        '''create final index.html symlink'''
        s = 'rm --verbose -- "{output.validsource}"'
        return self.shellscript(s, **kwargs)

    @classmethod
    def argparse(cls, p):
        descrip = 'executables and data files for %s' % (cls.formatname,)
        g = p.add_argument_group(title=cls.__name__, description=descrip)
        gadd = g.add_argument
        gadd('--docbook4xml-xslchunk', type=arg_isreadablefile,
             default=xslchunk_finder(),
             help='full path to LDP HTML chunker XSL [%(default)s]')
        gadd('--docbook4xml-xslsingle', type=arg_isreadablefile,
             default=xslsingle_finder(),
             help='full path to LDP HTML single-page XSL [%(default)s]')
        gadd('--docbook4xml-xslprint', type=arg_isstr,
             default=xslprint_finder(),
             help='full path to LDP FO print XSL [%(default)s]')
        gadd('--docbook4xml-xmllint', type=arg_isexecutable,
             default=which('xmllint'),
             help='full path to xmllint [%(default)s]')
        gadd('--docbook4xml-xsltproc', type=arg_isexecutable,
             default=which('xsltproc'),
             help='full path to xsltproc [%(default)s]')
        gadd('--docbook4xml-html2text', type=arg_isexecutable,
             default=which('html2text'),
             help='full path to html2text [%(default)s]')
        gadd('--docbook4xml-fop', type=arg_isexecutable,
             default=which('fop'),
             help='full path to fop [%(default)s]')
        gadd('--docbook4xml-dblatex', type=arg_isexecutable,
             default=which('dblatex'),
             help='full path to dblatex [%(default)s]')

#
# -- end of file
