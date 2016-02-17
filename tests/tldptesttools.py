
from __future__ import absolute_import, division, print_function

import os
import unittest
from tempfile import mkdtemp
import shutil


def stem_and_ext(name):
    stem, ext = os.path.splitext(os.path.basename(name))
    assert ext != ''
    return stem, ext


def dir_to_components(reldir):
    reldir, basename = os.path.split(os.path.normpath(reldir))
    components = [basename]
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

    def addfile(self, reldir, filename, stem=None, ext=None):
        if stem is None:
            stem, _ = stem_and_ext(filename)
        if ext is None:
            _, ext = stem_and_ext(filename)
        newname = os.path.join(self.tempdir, reldir, stem + ext)
        if os.path.isfile(filename):
            shutil.copy(filename, newname)
        else:
            with open(newname):
                pass
        relname = os.path.relpath(newname, self.tempdir)
        return relname, newname

#
# -- end of file
