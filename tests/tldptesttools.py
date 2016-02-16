
from __future__ import absolute_import, division, print_function

import os
import unittest
from tempfile import mkdtemp, mkstemp
import shutil

def stem_and_ext(name):
    stem, ext = os.path.splitext(os.path.basename(name))
    assert ext != ''
    return stem, ext

def dir_to_components(reldir):
    reldir = os.path.normpath(reldir)
    components = list()
    while reldir != '':
        reldir, basename = os.path.split(reldir)
        components.append(basename)
    assert len(components) >= 1
    components.reverse()
    return components


class TestToolsFilesystem(unittest.TestCase):

    def setUp(self):
        self.tempdir = mkdtemp(prefix='tldp-test-')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def adddir(self, reldir):
        components = dir_to_components(reldir)
        absdir = self.tempdir
        while components:
            absdir = os.path.join(absdir, components.pop(0))
            if not os.path.isdir(absdir):
                os.mkdir(absdir)
        self.assertTrue(os.path.isdir(absdir))
        relpath = os.path.relpath(absdir, self.tempdir)
        return relpath, absdir

    def addfile(self, dirname, exfile, stem=None, ext=None):
        if stem is None:
            stem, _ = stem_and_ext(exfile.filename)
        if ext is None:
            _, ext = stem_and_ext(exfile.filename)
        newname = os.path.join(dirname, stem + ext)
        shutil.copy(exfile.filename, newname)
        relname = os.path.relpath(newname, self.tempdir)
        return relname, newname

#
# -- end of file
