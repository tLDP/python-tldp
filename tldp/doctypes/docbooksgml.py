#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os

from tldp.utils import logger, which, execute, firstfoundfile
from tldp.utils import arg_isexecutable, isexecutable
from tldp.utils import arg_isreadablefile, isreadablefile

from tldp.doctypes.common import BaseDoctype, SignatureChecker


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


def config_fragment(p):
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

    buildorder = ['create_docindex_blank',
                  'create_docindex_data',
                  'create_docindex_full',
                  'move_docindex_to_source',
                  'create_htmls',
                  'create_pdf',
                  'create_txt',
                  'create_html',
                  'create_indexhtml',
                  ]

    # -- these names are (sort-of) chosen by the SGML toolchain
    docindex = 'index.sgml'
    docindexdata = 'HTML.index'

    def create_docindex_blank(self):
        stem = self.source.stem
        exe = collateindex = self.config.docbooksgml_collateindex
        outf = os.path.join(self.source.dirname, self.docindex)
        cmd = [collateindex, '-N', '-o', outf]
        logger.debug("%s creating blank %s (%s).", stem, outf, exe)
        result = execute(cmd, logdir=self.output.logdir)
        if result != 0:
            return False
        logger.info("%s created  blank %s.", stem, outf)
        return os.path.isfile(outf)

    def create_docindex_data(self):
        stem = self.source.stem
        exe = openjade = self.config.docbooksgml_openjade
        inf = self.source.filename
        if not os.path.exists(inf):
            return False
        outf = os.path.join(self.output.dirname, self.docindexdata)  # implicit
        cmd = [openjade, '-t', 'sgml', '-V', 'html-index', '-d',
               self.config.docbooksgml_docbookdsl, inf]
        logger.debug("%s creating idata %s (%s).", stem, outf, exe)
        result = execute(cmd, logdir=self.output.logdir)
        if result != 0:
            return False
        logger.info("%s created  idata %s.", stem, outf)
        return os.path.isfile(outf)

    def create_docindex_full(self):
        stem = self.source.stem
        exe = collateindex = self.config.docbooksgml_collateindex
        inf = self.source.filename
        docindexdata = os.path.join(self.output.dirname, self.docindexdata)
        if (not os.path.exists(inf)) or (not os.path.exists(docindexdata)):
            return False
        outf = os.path.join(self.output.dirname, self.docindex)
        cmd = [collateindex, '-g', '-t', 'Index', '-i', 'doc-index', '-o',
               outf, docindexdata, inf]
        logger.debug("%s creating index %s (%s).", stem, outf, exe)
        result = execute(cmd, logdir=self.output.logdir)
        if result != 0:
            return False
        logger.info("%s created  index %s.", stem, outf)
        return os.path.isfile(outf)

    def move_docindex_to_source(self):
        stem = self.source.stem
        source = os.path.join(self.output.dirname, self.docindex)
        target = os.path.join(self.source.dirname, self.docindex)
        if os.path.exists(target):
            try:
                os.unlink(target)
                logger.debug("%s unlinked index %s (old).", stem, target)
            except OSError:
                logger.debug("%s could not unlink old %s.", target)
        logger.debug("%s renaming index %s to %s.", stem, source, target)
        try:
            os.rename(source, target)
            logger.info("%s created  index %s (new).", stem, target)
        except OSError:
            logger.info("%s failed renaming %s (new).", stem, target)
        return os.path.isfile(target)

    def post_move_docindex_to_source(self):
        '''clear this directory (but no subdirectories)'''
        stem = self.source.stem
        dirname = self.output.dirname
        for name in os.listdir(dirname):
            fullname = os.path.join(dirname, name)
            if os.path.isfile(fullname):
                logger.debug("%s removing %s.", stem, fullname)
                os.unlink(fullname)
            else:
                logger.debug("%s not removing %s.", stem, fullname)
        return True

    def create_html(self):
        stem = self.source.stem
        exe = jw = self.config.docbooksgml_jw
        inf = self.source.filename
        if not os.path.exists(inf):
            return False
        outf = self.output.name_indexhtml
        cmd = [jw, '-f', 'docbook', '-b', 'html',
               '--dsl', self.config.docbooksgml_ldpdsl + '#html',
               '--output', '.', inf]
        logger.debug("%s creating HTML  %s (%s).", stem, outf, exe)
        result = execute(cmd, logdir=self.output.logdir)
        if result != 0:
            return False
        return os.path.isfile(outf)

    def post_create_html(self):
        stem = self.source.stem
        outf = self.output.name_html
        source = os.path.basename(self.output.name_indexhtml)
        target = os.path.basename(outf)
        logger.debug("%s renaming HTML  %s (from %s).", stem, outf, source)
        try:
            os.rename(source, target)
            logger.info("%s created  HTML  %s.", stem, outf)
        except OSError:
            logger.debug("%s failed renaming HTML file to %s.", stem, target)
        return os.path.isfile(outf)

    def create_htmls(self):
        stem = self.source.stem
        exe = jw = self.config.docbooksgml_jw
        inf = self.source.filename
        if not os.path.exists(inf):
            return False
        outf = self.output.name_html
        cmd = [jw, '-f', 'docbook', '-b', 'html', '-V', 'nochunks',
               '--dsl', self.config.docbooksgml_ldpdsl + '#html',
               '--output', '.', inf]
        logger.debug("%s creating HTMLS %s (%s).", stem, outf, exe)
        result = execute(cmd, logdir=self.output.logdir)
        if result != 0:
            return False
        return os.path.isfile(outf)

    def post_create_htmls(self):
        stem = self.source.stem
        outf = self.output.name_htmls
        source = os.path.basename(self.output.name_html)
        target = os.path.basename(outf)
        logger.debug("%s renaming HTMLS to %s.", stem, target)
        try:
            os.rename(source, target)
            logger.info("%s created  HTMLS %s.", stem, outf)
        except OSError:
            logger.debug("%s failed renaming HTML single file to %s.",
                         stem, target)
        return os.path.isfile(outf)

    def create_indexhtml(self):
        stem = self.source.stem
        outf = self.output.name_html
        target = os.path.basename(outf)
        linkname = self.output.name_indexhtml
        symlink = os.path.basename(linkname)
        logger.debug("%s creating index.html symlink to %s.", stem, target)
        try:
            os.symlink(target, symlink)
            logger.info("%s created  link  %s to %s.", stem, linkname, target)
        except OSError:
            logger.debug("%s failed in creating index.html symlink.", stem)
        return os.path.islink(linkname)

    def create_pdf(self):
        stem = self.source.stem
        exe = jw = self.config.docbooksgml_jw
        inf = self.source.filename
        if not os.path.exists(inf):
            return False
        outf = self.output.name_pdf
        cmd = [jw, '-f', 'docbook', '-b', 'pdf', '--output', '.', inf]
        logger.debug("%s creating PDF   %s (%s).", stem, outf, exe)
        result = execute(cmd, logdir=self.output.logdir)
        if result != 0:
            return self.create_pdf_alternate()
        logger.info("%s created  PDF   %s (%s).", stem, outf, exe)
        return os.path.isfile(outf)

    def create_pdf_alternate(self):
        stem = self.source.stem
        exe = dblatex = self.config.docbooksgml_dblatex
        inf = self.source.filename
        if not os.path.exists(inf):
            return False
        outf = self.output.name_pdf
        cmd = [dblatex, '-F', 'sgml', '-t', 'pdf', '-o', outf, inf]
        logger.debug("%s creating PDF   %s (%s).", stem, outf, exe)
        result = execute(cmd, logdir=self.output.logdir)
        if result != 0:
            return False
        logger.info("%s created  PDF   %s (%s).", stem, outf, exe)
        return os.path.isfile(outf)

    def create_txt(self):
        stem = self.source.stem
        exe = html2text = self.config.docbooksgml_html2text
        inf = self.output.name_htmls
        if not os.path.exists(inf):
            return False
        outf = self.output.name_txt
        cmd = [html2text, '-style', 'pretty', '-nobs', inf]
        logger.debug("%s creating TXT   %s (%s).", stem, outf, exe)
        with open(outf, 'wx') as stdout:
            result = execute(cmd, logdir=self.output.logdir, stdout=stdout)
        if result != 0:
            return False
        logger.info("%s created  TXT   %s.", stem, outf)
        return os.path.isfile(outf)

#
# -- end of file
