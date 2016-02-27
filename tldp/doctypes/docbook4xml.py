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

    graph = nx.DiGraph()

    buildorder = ['buildall']

    def chdir_output(self):
        os.chdir(self.output.dirname)
        return True

    @depends(graph, chdir_output)
    def copy_static_resources(self):
        source = list()
        for d in ('images', 'resources'):
            fullpath = os.path.join(self.source.dirname, d)
            fullpath = os.path.abspath(fullpath)
            if os.path.isdir(fullpath):
                source.append('"' + fullpath + '"')
            if not source:
                logger.debug("%s no images or resources to copy", self.source.stem)
                return True
            s = 'rsync --archive --verbose %s ./' % (' '.join(source))
        return self.shellscript(s)

    @depends(graph, copy_static_resources)
    def make_name_htmls(self):
        '''create a single page HTML output'''
        s = '''"{config.docbook4xml_xsltproc}" > "{output.name_htmls}" \\
                  --nonet \\
                  --stringparam admon.graphics.path images/ \\
                  --stringparam base.dir . \\
                  "{config.docbook4xml_xslsingle}" \\
                  "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, make_name_htmls)
    def make_name_txt(self):
        '''create text output'''
        s = '''"{config.docbook4xml_html2text}" > "{output.name_txt}" \\
                  -style pretty \\
                  -nobs \\
                  "{output.name_htmls}"'''
        return self.shellscript(s)

    @depends(graph, chdir_output)
    def make_fo(self):
        '''generate the Formatting Objects intermediate output'''
        s = '''"{config.docbook4xml_xsltproc}" > "{output.name_fo}" \\
                  "{config.docbook4xml_xslprint}" \\
                  "{source.filename}"'''
        self.removals.append(self.output.name_fo)
        return self.shellscript(s)

    # -- this is conditionally built--see logic in make_name_pdf() below
    # @depends(graph, make_fo)
    def make_pdf_with_fop(self):
        '''use FOP to create a PDF'''
        s = '''"{config.docbook4xml_fop}" \\
                  -fo "{output.name_fo}" \\
                  -pdf "{output.name_pdf}"'''
        return self.shellscript(s)

    # -- this is conditionally built--see logic in make_name_pdf() below
    # @depends(graph, chdir_output)
    def make_pdf_with_dblatex(self):
        '''use dblatex (fallback) to create a PDF'''
        s = '''"{config.docbook4xml_dblatex}" \\
                  -F xml \\
                  -t pdf \\
                  -o "{output.name_pdf}" \\
                  "{source.filename}"'''
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
                     stem, self.config.docbook4xml_fop)
        logger.info("%s calling method %s.%s",
                    stem, classname, 'make_pdf_with_dblatex')
        return self.make_pdf_with_dblatex()

    @depends(graph, make_name_htmls)
    def make_html(self):
        '''create chunked HTML output'''
        s = '''"{config.docbook4xml_xsltproc}" \\
                  --nonet \\
                  --stringparam admon.graphics.path images/ \\
                  --stringparam base.dir . \\
                  "{config.docbook4xml_xslchunk}" \\
                  "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, make_html)
    def make_name_html(self):
        '''rename xsltproc/docbook-XSL's index.html to LDP standard STEM.html'''
        s = 'mv -v --no-clobber -- "{output.name_indexhtml}" "{output.name_html}"'
        return self.shellscript(s)

    @depends(graph, make_name_html)
    def make_name_indexhtml(self):
        '''create final index.html symlink'''
        s = 'ln -svr -- "{output.name_html}" "{output.name_indexhtml}"'
        return self.shellscript(s)

    @classmethod
    def argparse(cls, p):
        descrip = 'executables and data files for %s' % (cls.formatname,)
        g = p.add_argument_group(title=cls.__name__, description=descrip)
        g.add_argument('--docbook4xml-xslchunk', type=arg_isreadablefile,
                       default=xslchunk_finder(),
                       help='full path to LDP HTML chunker XSL [%(default)s]')
        g.add_argument('--docbook4xml-xslsingle', type=arg_isreadablefile,
                       default=xslsingle_finder(),
                       help='full path to LDP HTML single-page XSL [%(default)s]')
        g.add_argument('--docbook4xml-xslprint', type=arg_isreadablefile,
                       default=xslprint_finder(),
                       help='full path to LDP FO print XSL [%(default)s]')
        g.add_argument('--docbook4xml-xsltproc', type=arg_isexecutable,
                       default=which('xsltproc'),
                       help='full path to xsltproc [%(default)s]')
        g.add_argument('--docbook4xml-html2text', type=arg_isexecutable,
                       default=which('html2text'),
                       help='full path to html2text [%(default)s]')
        g.add_argument('--docbook4xml-fop', type=arg_isexecutable,
                       default=which('fop'),
                       help='full path to fop [%(default)s]')
        g.add_argument('--docbook4xml-dblatex', type=arg_isexecutable,
                       default=which('dblatex'),
                       help='full path to dblatex [%(default)s]')

#
# -- end of file
