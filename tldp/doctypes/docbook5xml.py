#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import logging

import networkx as nx

from tldp.utils import which, firstfoundfile
from tldp.utils import arg_isexecutable, isexecutable
from tldp.utils import arg_isreadablefile, isreadablefile

from tldp.doctypes.common import BaseDoctype, SignatureChecker, depends

logger = logging.getLogger(__name__)


def rngfile_finder():
    l = ['/usr/share/xml/docbook/schema/rng/5.0/docbook.rng',
         ]
    return firstfoundfile(l)


def xslchunk_finder():
    l = ['/usr/share/xml/docbook/stylesheet/nwalsh5/current/html/chunk.xsl',
         '/usr/share/xml/docbook/stylesheet/docbook-xsl-ns/html/chunk.xsl',
         'http://docbook.sourceforge.net/release/xsl/current/html/chunk.xsl',
         ]
    return firstfoundfile(l)


def xslsingle_finder():
    l = ['/usr/share/xml/docbook/stylesheet/nwalsh5/current/html/docbook.xsl',
         '/usr/share/xml/docbook/stylesheet/docbook-xsl-ns/html/docbook.xsl',
         'http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl',
         ]
    return firstfoundfile(l)


def xslprint_finder():
    l = ['/usr/share/xml/docbook/stylesheet/nwalsh5/current/fo/docbook.xsl',
         '/usr/share/xml/docbook/stylesheet/docbook-xsl-ns/fo/docbook.xsl',
         'http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl',
         ]
    return firstfoundfile(l)


class Docbook5XML(BaseDoctype, SignatureChecker):
    formatname = 'DocBook XML 5.x'
    extensions = ['.xml']
    signatures = ['-//OASIS//DTD DocBook V5.0/EN',
                  'http://docbook.org/ns/docbook', ]

    required = {'docbook5xml_xsltproc': isexecutable,
                'docbook5xml_xmllint': isexecutable,
                'docbook5xml_html2text': isexecutable,
                'docbook5xml_dblatex': isexecutable,
                'docbook5xml_fop': isexecutable,
                'docbook5xml_jing': isexecutable,
                'docbook5xml_rngfile': isreadablefile,
                'docbook5xml_xslprint': isreadablefile,
                'docbook5xml_xslchunk': isreadablefile,
                'docbook5xml_xslsingle': isreadablefile,
                }

    graph = nx.DiGraph()

    def chdir_output(self):
        os.chdir(self.output.dirname)
        return True

    @depends(graph, chdir_output)
    def validate_source(self):
        '''consider lxml.etree and other validators'''
        s = '''"{config.docbook5xml_jing}" \\
                  "{config.docbook5xml_rngfile}" \\
                  "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, validate_source)
    def make_xincluded_source(self):
        s = '''"{config.docbook5xml_xmllint}" > "{output.validsource}" \\
                  --nonet \\
                  --noent \\
                  --xinclude \\
                  "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, make_xincluded_source)
    def copy_static_resources(self):
        source = list()
        for d in ('images', 'resources'):
            fullpath = os.path.join(self.source.dirname, d)
            fullpath = os.path.abspath(fullpath)
            if os.path.isdir(fullpath):
                source.append('"' + fullpath + '"')
            if not source:
                logger.debug("%s no images or resources to copy",
                             self.source.stem)
                return True
            s = 'rsync --archive --verbose %s ./' % (' '.join(source))
        return self.shellscript(s)

    @depends(graph, copy_static_resources)
    def make_name_htmls(self):
        '''create a single page HTML output'''
        s = '''"{config.docbook5xml_xsltproc}" > "{output.name_htmls}" \\
                  --nonet \\
                  --stringparam admon.graphics.path images/ \\
                  --stringparam base.dir . \\
                  "{config.docbook5xml_xslsingle}" \\
                  "{output.validsource}"'''
        return self.shellscript(s)

    @depends(graph, make_name_htmls)
    def make_name_txt(self):
        '''create text output'''
        s = '''"{config.docbook5xml_html2text}" > "{output.name_txt}" \\
                  -style pretty \\
                  -nobs \\
                  "{output.name_htmls}"'''
        return self.shellscript(s)

    @depends(graph, copy_static_resources)
    def make_fo(self):
        '''generate the Formatting Objects intermediate output'''
        s = '''"{config.docbook5xml_xsltproc}" > "{output.name_fo}" \\
                  "{config.docbook5xml_xslprint}" \\
                  "{output.validsource}"'''
        self.removals.append(self.output.name_fo)
        return self.shellscript(s)

    # -- this is conditionally built--see logic in make_name_pdf() below
    # @depends(graph, make_fo)
    def make_pdf_with_fop(self):
        '''use FOP to create a PDF'''
        s = '''"{config.docbook5xml_fop}" \\
                  -fo "{output.name_fo}" \\
                  -pdf "{output.name_pdf}"'''
        return self.shellscript(s)

    # -- this is conditionally built--see logic in make_name_pdf() below
    # @depends(graph, chdir_output)
    def make_pdf_with_dblatex(self):
        '''use dblatex (fallback) to create a PDF'''
        s = '''"{config.docbook5xml_dblatex}" \\
                  -F xml \\
                  -t pdf \\
                  -o "{output.name_pdf}" \\
                  "{output.validsource}"'''
        return self.shellscript(s)

    @depends(graph, make_fo)
    def make_name_pdf(self):
        stem = self.source.stem
        classname = self.__class__.__name__
        logger.info("%s calling method %s.%s",
                    stem, classname, 'make_pdf_with_fop')
        if self.make_pdf_with_fop():
            return True
        logger.error("%s %s failed creating PDF, falling back to dblatex...",
                     stem, self.config.docbook5xml_fop)
        logger.info("%s calling method %s.%s",
                    stem, classname, 'make_pdf_with_dblatex')
        return self.make_pdf_with_dblatex()

    @depends(graph, make_name_htmls)
    def make_html(self):
        '''create chunked HTML output'''
        s = '''"{config.docbook5xml_xsltproc}" \\
                  --nonet \\
                  --stringparam admon.graphics.path images/ \\
                  --stringparam base.dir . \\
                  "{config.docbook5xml_xslchunk}" \\
                  "{output.validsource}"'''
        return self.shellscript(s)

    @depends(graph, make_html)
    def make_name_html(self):
        '''rename DocBook XSL's index.html to LDP standard STEM.html'''
        s = 'mv -v --no-clobber -- "{output.name_indexhtml}" "{output.name_html}"'
        return self.shellscript(s)

    @depends(graph, make_name_html)
    def make_name_indexhtml(self):
        '''create final index.html symlink'''
        s = 'ln -svr -- "{output.name_html}" "{output.name_indexhtml}"'
        return self.shellscript(s)

    @depends(graph, make_name_indexhtml, make_name_pdf)
    def remove_xincluded_source(self):
        '''remove the xincluded source file'''
        s = 'rm --verbose -- "{output.validsource}"'
        return self.shellscript(s)

    @classmethod
    def argparse(cls, p):
        descrip = 'executables for %s' % (cls.formatname,)
        g = p.add_argument_group(title=cls.__name__, description=descrip)
        g.add_argument('--docbook5xml-xslchunk', type=arg_isreadablefile,
                       default=xslchunk_finder(),
                       help='full path to LDP HTML chunker XSL [%(default)s]')
        g.add_argument('--docbook5xml-xslsingle', type=arg_isreadablefile,
                       default=xslsingle_finder(),
                       help='full path to LDP HTML single-page XSL [%(default)s]')
        g.add_argument('--docbook5xml-xslprint', type=arg_isreadablefile,
                       default=xslprint_finder(),
                       help='full path to LDP FO print XSL [%(default)s]')

        g.add_argument('--docbook5xml-rngfile', type=arg_isreadablefile,
                       default=rngfile_finder(),
                       help='full path to docbook.rng [%(default)s]')
        g.add_argument('--docbook5xml-xmllint', type=arg_isexecutable,
                       default=which('xmllint'),
                       help='full path to xmllint [%(default)s]')
        g.add_argument('--docbook5xml-xsltproc', type=arg_isexecutable,
                       default=which('xsltproc'),
                       help='full path to xsltproc [%(default)s]')
        g.add_argument('--docbook5xml-html2text', type=arg_isexecutable,
                       default=which('html2text'),
                       help='full path to html2text [%(default)s]')
        g.add_argument('--docbook5xml-fop', type=arg_isexecutable,
                       default=which('fop'),
                       help='full path to fop [%(default)s]')
        g.add_argument('--docbook5xml-dblatex', type=arg_isexecutable,
                       default=which('dblatex'),
                       help='full path to dblatex [%(default)s]')
        g.add_argument('--docbook5xml-jing', type=arg_isexecutable,
                       default=which('jing'),
                       help='full path to jing [%(default)s]')


#
# -- end of file
