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


def docbookdsl_finder():
    locations = [
      '/usr/share/sgml/docbook/stylesheet/dsssl/modular/html/docbook.dsl',
      '/usr/share/sgml/docbook/dsssl-stylesheets/html/docbook.dsl',
      ]
    return firstfoundfile(locations)


def ldpdsl_finder():
    locations = [
      '/usr/share/sgml/docbook/stylesheet/dsssl/ldp/ldp.dsl',
      ]
    return firstfoundfile(locations)


class DocbookSGML(BaseDoctype, SignatureChecker):
    formatname = 'DocBook SGML 3.x/4.x'
    extensions = ['.sgml']
    signatures = ['-//Davenport//DTD DocBook V3.0//EN',
                  '-//OASIS//DTD DocBook V3.1//EN',
                  '-//OASIS//DTD DocBook V4.1//EN',
                  '-//OASIS//DTD DocBook V4.2//EN', ]

    required = {'docbooksgml_jw': isexecutable,
                'docbooksgml_openjade': isexecutable,
                'docbooksgml_dblatex': isexecutable,
                'docbooksgml_html2text': isexecutable,
                'docbooksgml_collateindex': isexecutable,
                'docbooksgml_ldpdsl': isreadablefile,
                'docbooksgml_docbookdsl': isreadablefile,
                }

    graph = nx.DiGraph()

    buildorder = ['buildall']

    def chdir_output(self):
        os.chdir(self.output.dirname)
        return True

    @depends(graph, chdir_output)
    def make_blank_indexsgml(self):
        '''generate an empty index.sgml file (in output dir)'''
        s = '''"{config.docbooksgml_collateindex}" \\
                  -N \\
                  -o \\
                  "index.sgml"'''
        return self.shellscript(s)

    @depends(graph, make_blank_indexsgml)
    def make_data_indexsgml(self):
        '''collect document's index entries into a data file (HTML.index)'''
        s = '''"{config.docbooksgml_openjade}" \\
                  -t sgml \\
                  -V html-index \\
                  -d "{config.docbooksgml_docbookdsl}" \\
                  "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, make_data_indexsgml)
    def make_indexsgml(self):
        '''generate the final document index file (index.sgml)'''
        s = '''"{config.docbooksgml_collateindex}" \\
                  -g \\
                  -t Index \\
                  -i doc-index \\
                  -o "index.sgml" \\
                     "HTML.index" \\
                     "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, make_indexsgml)
    def move_indexsgml_into_source(self):
        '''move the generated index.sgml file into the source tree'''
        indexsgml = os.path.join(self.source.dirname, 'index.sgml')
        s = '''mv \\
                 --no-clobber \\
                 --verbose \\
                 -- "index.sgml" "{source.dirname}/index.sgml"'''
        moved = self.shellscript(s)
        if moved:
            self.removals = indexsgml
            logger.debug("%s created %s", self.source.stem, indexsgml)
            return True
        return os.path.exists(indexsgml)

    @depends(graph, move_indexsgml_into_source)
    def cleaned_indexsgml(self):
        '''clean the junk from the output dir after building the index.sgml'''
        # -- be super cautious before removing a bunch of files
        cwd = os.getcwd()
        if not os.path.samefile(cwd, self.output.dirname):
            logger.error("%s (cowardly) refusing to clean directory %s", cwd)
            logger.error("%s expected to find %s", self.output.dirname)
            return False
        s = '''find . -mindepth 1 -maxdepth 1 -type f -print0 \
               | xargs --null --no-run-if-empty -- rm -f --'''
        return self.shellscript(s)

    @depends(graph, cleaned_indexsgml)
    def make_htmls(self):
        '''create a single page HTML output (with incorrect name)'''
        s = '''"{config.docbooksgml_jw}" \\
                  -f docbook \\
                  -b html \\
                  --dsl "{config.docbooksgml_ldpdsl}#html" \\
                  -V nochunks \\
                  -V '%callout-graphics-path%=images/callouts/' \\
                  -V '%stock-graphics-extension%=.png' \\
                  --output . \\
                  "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, make_htmls)
    def make_name_htmls(self):
        '''correct the single page HTML output name'''
        s = 'mv -v --no-clobber -- "{output.name_html}" "{output.name_htmls}"'
        return self.shellscript(s)

    @depends(graph, make_name_htmls)
    def make_name_txt(self):
        '''create text output (from single-page HTML)'''
        s = '''"{config.docbooksgml_html2text}" > "{output.name_txt}" \\
                  -style pretty \\
                  -nobs \\
                  "{output.name_htmls}"'''
        return self.shellscript(s)

    def make_pdf_with_jw(self):
        s = '''"{config.docbooksgml_jw}" \\
                  -f docbook \\
                  -b pdf \\
                  --output . \\
                  "{source.filename}"'''
        return self.shellscript(s)

    def make_pdf_with_dblatex(self):
        s = '''"{config.docbooksgml_dblatex}" \\
                  -F sgml \\
                  -t pdf \\
                  -o "{output.name_pdf}" \\
                     "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, cleaned_indexsgml)
    def make_name_pdf(self):
        if self.make_pdf_with_jw():
             return True
        return self.make_pdf_with_dblatex()

    @depends(graph, make_name_htmls)
    def make_html(self):
        '''create final index.html symlink'''
        s = '''"{config.docbooksgml_jw}" \\
                 -f docbook \\
                 -b html \\
                 --dsl "{config.docbooksgml_ldpdsl}#html" \\
                 -V '%callout-graphics-path%=images/callouts/' \\
                 -V '%stock-graphics-extension%=.png' \\
                 --output . \\
                 "{source.filename}"'''
        return self.shellscript(s)

    @depends(graph, make_html)
    def make_name_html(self):
        '''rename openjade's index.html to LDP standard name STEM.html'''
        s = 'mv -v --no-clobber -- "{output.name_indexhtml}" "{output.name_html}"'
        return self.shellscript(s)

    @depends(graph, make_name_html)
    def make_name_indexhtml(self):
        '''create final index.html symlink'''
        s = 'ln -svr -- "{output.name_html}" "{output.name_indexhtml}"'
        return self.shellscript(s)

    @staticmethod
    def argparse(p):
        p.add_argument('--docbooksgml-docbookdsl', type=arg_isreadablefile,
                       default=docbookdsl_finder(),
                       help='full path to html/docbook.dsl [%(default)s]')
        p.add_argument('--docbooksgml-ldpdsl', type=arg_isreadablefile,
                       default=ldpdsl_finder(),
                       help='full path to ldp/ldp.dsl [%(default)s]')
        p.add_argument('--docbooksgml-jw', type=arg_isexecutable,
                       default=which('jw'),
                       help='full path to jw [%(default)s]')
        p.add_argument('--docbooksgml-html2text', type=arg_isexecutable,
                       default=which('html2text'),
                       help='full path to html2text [%(default)s]')
        p.add_argument('--docbooksgml-openjade', type=arg_isexecutable,
                       default=which('openjade'),
                       help='full path to openjade [%(default)s]')
        p.add_argument('--docbooksgml-dblatex', type=arg_isexecutable,
                       default=which('dblatex'),
                       help='full path to dblatex [%(default)s]')
        p.add_argument('--docbooksgml-collateindex', type=arg_isexecutable,
                       default=which('collateindex'),
                       help='full path to collateindex [%(default)s]')



#
# -- end of file
