
from __future__ import absolute_import, division, print_function

import os
import errno
import unittest
from tempfile import NamedTemporaryFile as ntf
from tempfile import mkdtemp, mkstemp
import shutil
import random

try:
    from types import SimpleNamespace
except ImportError:
    from utils import SimpleNamespace

# -- Test Data
import examples

# -- SUT
from tldp.sources import SourceCollection, SourceDocument

datadir = os.path.join(os.path.dirname(__file__), 'testdata')


def stem_and_ext(name):
    stem, ext = os.path.splitext(os.path.basename(name))
    assert ext != ''
    return stem, ext


class TestSourceCollection(unittest.TestCase):

    def setUp(self):
        self.tempdir = mkdtemp(prefix='tldp-sources-test-')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def mkdir_components(self, components):
        dirname = self.tempdir
        assert len(components) >= 1
        while components:
            dirname = os.path.join(dirname, components.pop(0))
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
        self.assertTrue(os.path.isdir(dirname))
        relpath = os.path.relpath(dirname, self.tempdir)
        return relpath, dirname

    def addfile(self, dirname, exfile, stem=None, ext=None):
        if stem is None:
            stem, _ = stem_and_ext(exfile.filename)
        if ext is None:
            _, ext = stem_and_ext(exfile.filename)
        newname = os.path.join(dirname, stem + ext)
        shutil.copy(exfile.filename, newname)
        relname = os.path.relpath(newname, self.tempdir)
        return relname, newname


class TestFileSourceCollectionMultiDir(TestSourceCollection):

    def test_multidir_finding_singlefiles(self):
        ex = random.choice(examples.examples)
        doc0 = SimpleNamespace(stem="A-Unique-Stem", components=['LDP', 'howto'])
        doc1 = SimpleNamespace(stem="A-Different-Stem", components=['LDP', 'guide'])
        documents = (doc0, doc1)
        for d in documents:
            d.reldir, d.absdir = self.mkdir_components(d.components)
            d.relname, d.absname = self.addfile(d.absdir, ex, stem=d.stem)
        s = SourceCollection([x.absdir for x in documents])
        self.assertEquals(2, len(s))
        sought = set([x.stem for x in documents])
        found = set([x for x in s])
        self.assertEquals(sought, found)


class TestFileSourceCollectionOneDir(TestSourceCollection):

    def test_finding_singlefile(self):
        ex = random.choice(examples.examples)
        maindir = ['LDP', 'LDP', 'howto']
        reldir, absdir = self.mkdir_components(maindir)
        _, _ = self.addfile(absdir, ex)
        s = SourceCollection([absdir])
        self.assertEquals(1, len(s))

    def test_skipping_misnamed_singlefile(self):
        ex = random.choice(examples.examples)
        maindir = ['LDP', 'LDP', 'howto']
        reldir, absdir = self.mkdir_components(maindir)
        self.addfile(absdir, ex, ext=".mis")
        s = SourceCollection([absdir])
        self.assertEquals(1, len(s))


class TestInvalidSourceCollection(TestSourceCollection):

    def test_validateDirs_onebad(self):
        invalid0 = os.path.join(self.tempdir, 'unique', 'rabbit')
        with self.assertRaises(IOError) as ecm:
            SourceCollection([invalid0])
        e = ecm.exception
        self.assertTrue('unique/rabbit' in e.filename)

    def test_validateDirs_multibad(self):
        invalid0 = os.path.join(self.tempdir, 'unique', 'rabbit')
        invalid1 = os.path.join(self.tempdir, 'affable', 'elephant')
        with self.assertRaises(IOError) as ecm:
            SourceCollection([invalid0, invalid1])
        e = ecm.exception
        self.assertTrue('affable/elephant' in e.filename)

    def testEmptyDir(self):
        s = SourceCollection([self.tempdir])
        import pprint
        pprint.pprint(s.__dict__)
        self.assertEquals(0, len(s))


class TestMissingSourceDocuments(TestSourceCollection):

    def test_init_missing(self):
        missing = os.path.join(self.tempdir, 'vanishing')
        with self.assertRaises(IOError) as ecm:
            SourceDocument(missing)
        e = ecm.exception
        self.assertEquals(errno.ENOENT, e.errno)

        with self.assertRaises(TypeError) as ecm:
            SourceDocument(self.tempdir)
        e = ecm.exception
        self.assertTrue('Wrong type' in e.message)

#
# -- end of file
