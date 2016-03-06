#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import logging

from tldp.utils import which
from tldp.utils import arg_isexecutable, isexecutable
from tldp.doctypes.common import BaseDoctype, depends

logger = logging.getLogger(__name__)


class Asciidoc(BaseDoctype):
    formatname = 'AsciiDoc'
    extensions = ['.txt']
    signatures = []

    required = {'asciidoc_sgml2html': isexecutable,
                'asciidoc_html2text': isexecutable,
                'asciidoc_htmldoc': isexecutable,
                'asciidoc_a2x': isexecutable,
                }

    def chdir_output(self):
        os.chdir(self.output.dirname)
        return True

    @depends(chdir_output)
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

    @depends(chdir_output)
    def make_name_pdf(self):
        s = '''"{config.asciidoc_a2x}" \\
                 --verbose \\
                 --format pdf \\
                 --destination-dir . \\
                 "{source.filename}"'''
        return self.shellscript(s)

    @depends(chdir_output)
    def make_name_txt(self):
        s = 'cp --verbose --target-directory . -- "{source.filename}"'
        return self.shellscript(s)

    @depends(chdir_output)
    def make_name_htmls(self):
        s = '''"{config.asciidoc_a2x}" \\
                 --verbose \\
                 --format xhtml \\
                 --destination-dir . \\
                 "{source.filename}"'''
        return self.shellscript(s)

    @depends(chdir_output)
    def make_chunked_html(self):
        s = '''"{config.asciidoc_a2x}" \\
                 --verbose \\
                 --format chunked \\
                 --destination-dir . \\
                 "{source.filename}"'''
        return self.shellscript(s)

    @depends(make_chunked_html)
    def move_chunked_html(self):
        s = 'mv --no-clobber -v -- "{output.stem}.chunked" html'
        return self.shellscript(s)

    @depends(move_chunked_html)
    def make_name_html(self):
        s = 'ln -sv --relative -- html/index.html {output.name_indexhtml}'
        return self.shellscript(s)

    @classmethod
    def argparse(cls, p):
        descrip = 'executables and data files for %s' % (cls.formatname,)
        g = p.add_argument_group(title=cls.__name__, description=descrip)
        g.add_argument('--asciidoc-a2x', type=arg_isexecutable,
                       default=which('a2x'),
                       help='full path to a2x [%(default)s]')

#
# -- end of file
