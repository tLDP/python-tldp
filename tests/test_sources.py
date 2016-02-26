
from __future__ import absolute_import, division, print_function

import os
import errno
import random
import unittest

try:
    from types import SimpleNamespace
except ImportError:
    from utils import SimpleNamespace

from tldptesttools import TestToolsFilesystem

# -- Test Data
import example

# -- SUT
from tldp.sources import SourceCollection, SourceDocument, scansourcedirs

datadir = os.path.join(os.path.dirname(__file__), 'sample-documents')


class TestFileSourceCollectionMultiDir(TestToolsFilesystem):

    def test_multidir_finding_singlefiles(self):
        ex = random.choice(example.sources)
        doc0 = SimpleNamespace(reldir='LDP/howto', stem="A-Unique-Stem")
        doc1 = SimpleNamespace(reldir='LDP/guide', stem="A-Different-Stem")
        documents = (doc0, doc1)
        for d in documents:
            d.reldir, d.absdir = self.adddir(d.reldir)
            _, _ = self.addfile(d.reldir, ex.filename, stem=d.stem)
        s = scansourcedirs([x.absdir for x in documents])
        self.assertEquals(2, len(s))
        expected = set([x.stem for x in documents])
        found = set(s.keys())
        self.assertEquals(expected, found)

    def test_multidir_finding_namecollision(self):
        ex = random.choice(example.sources)
        doc0 = SimpleNamespace(reldir='LDP/howto', stem="A-Non-Unique-Stem")
        doc1 = SimpleNamespace(reldir='LDP/guide', stem="A-Non-Unique-Stem")
        documents = (doc0, doc1)
        for d in documents:
            d.reldir, d.absdir = self.adddir(d.reldir)
            _, _ = self.addfile(d.reldir, ex.filename, stem=d.stem)
        s = scansourcedirs([x.absdir for x in documents])
        self.assertEquals(1, len(s))
        expected = set([x.stem for x in documents])
        found = set(s.keys())
        self.assertEquals(expected, found)


class TestFileSourceCollectionOneDir(TestToolsFilesystem):

    def test_finding_nonfile(self):
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        os.mkfifo(os.path.join(absdir, 'non-dir-non-file.rst'))
        s = scansourcedirs([absdir])
        self.assertEquals(0, len(s))

    def test_finding_singlefile(self):
        ex = random.choice(example.sources)
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        _, _ = self.addfile(reldir, ex.filename)
        s = scansourcedirs([absdir])
        self.assertEquals(1, len(s))

    def test_skipping_misnamed_singlefile(self):
        ex = random.choice(example.sources)
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        self.addfile(reldir, ex.filename, ext=".mis")
        s = scansourcedirs([absdir])
        self.assertEquals(1, len(s))

    def test_multiple_stems_of_different_extensions(self):
        ex = random.choice(example.sources)
        stem = 'A-Non-Unique-Stem'
        maindir = os.path.join('LDP/LDP/howto', stem)
        reldir, absdir = self.adddir(maindir)
        self.addfile(reldir, ex.filename, stem=stem, ext=".xml")
        self.addfile(reldir, ex.filename, stem=stem, ext=".md")
        s = scansourcedirs([absdir])
        self.assertEquals(1, len(s))


class TestNullSourceCollection(TestToolsFilesystem):

    def test_SourceCollection_no_dirnames(self):
        s = SourceCollection()
        self.assertIsInstance(s, SourceCollection)


class TestInvalidSourceCollection(TestToolsFilesystem):

    def test_validateDirs_onebad(self):
        invalid0 = os.path.join(self.tempdir, 'unique', 'rabbit')
        with self.assertRaises(IOError) as ecm:
            scansourcedirs([invalid0])
        e = ecm.exception
        self.assertTrue('unique/rabbit' in e.filename)

    def test_validateDirs_multibad(self):
        invalid0 = os.path.join(self.tempdir, 'unique', 'rabbit')
        invalid1 = os.path.join(self.tempdir, 'affable', 'elephant')
        with self.assertRaises(IOError) as ecm:
            scansourcedirs([invalid0, invalid1])
        e = ecm.exception
        self.assertTrue('affable/elephant' in e.filename)

    def testEmptyDir(self):
        s = scansourcedirs([self.tempdir])
        self.assertEquals(0, len(s))


class TestSourceDocuments(unittest.TestCase):

    def test_init_missing(self):
        doc = SourceDocument(os.path.join(datadir, 'linuxdoc-simple.sgml'))
        self.assertIsInstance(doc, SourceDocument)
        self.assertTrue("linuxdoc-simple.sgml" in str(doc))


class TestMissingSourceDocuments(TestToolsFilesystem):

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
