
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

from tldptesttools import *

# -- Test Data
import examples

# -- SUT
from tldp.sources import SourceCollection, SourceDocument

datadir = os.path.join(os.path.dirname(__file__), 'testdata')


class TestFileSourceCollectionMultiDir(TestToolsFilesystem):

    def test_multidir_finding_singlefiles(self):
        ex = random.choice(examples.sources)
        doc0 = SimpleNamespace(reldir='LDP/howto', stem="A-Unique-Stem")
        doc1 = SimpleNamespace(reldir='LDP/guide', stem="A-Different-Stem")
        documents = (doc0, doc1)
        for d in documents:
            d.reldir, d.absdir = self.adddir(d.reldir)
            d.relname, d.absname = self.addfile(d.absdir, ex, stem=d.stem)
        s = SourceCollection([x.absdir for x in documents])
        self.assertEquals(2, len(s))
        expected = set([x.stem for x in documents])
        found = set(s.keys())
        self.assertEquals(expected, found)

    def test_multidir_finding_namecollision(self):
        ex = random.choice(examples.sources)
        doc0 = SimpleNamespace(reldir='LDP/howto', stem="A-Non-Unique-Stem")
        doc1 = SimpleNamespace(reldir='LDP/guide', stem="A-Non-Unique-Stem")
        documents = (doc0, doc1)
        for d in documents:
            d.reldir, d.absdir = self.adddir(d.reldir)
            d.relname, d.absname = self.addfile(d.absdir, ex, stem=d.stem)
        s = SourceCollection([x.absdir for x in documents])
        self.assertEquals(1, len(s))
        expected = set([x.stem for x in documents])
        found = set(s.keys())
        self.assertEquals(expected, found)


class TestFileSourceCollectionOneDir(TestToolsFilesystem):

    def test_finding_nonfile(self):
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        os.mkfifo(os.path.join(absdir, 'non-dir-non-file.rst'))
        s = SourceCollection([absdir])
        self.assertEquals(0, len(s))

    def test_finding_singlefile(self):
        ex = random.choice(examples.sources)
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        _, _ = self.addfile(absdir, ex)
        s = SourceCollection([absdir])
        self.assertEquals(1, len(s))

    def test_skipping_misnamed_singlefile(self):
        ex = random.choice(examples.sources)
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        self.addfile(absdir, ex, ext=".mis")
        s = SourceCollection([absdir])
        self.assertEquals(1, len(s))

    def test_multiple_stems_of_different_extensions(self):
        ex = random.choice(examples.sources)
        stem = 'A-Non-Unique-Stem'
        maindir = os.path.join('LDP/LDP/howto', stem)
        reldir, absdir = self.adddir(maindir)
        self.addfile(absdir, ex, stem=stem, ext=".xml")
        self.addfile(absdir, ex, stem=stem, ext=".md")
        s = SourceCollection([absdir])
        self.assertEquals(1, len(s))


class TestInvalidSourceCollection(TestToolsFilesystem):

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
        self.assertEquals(0, len(s))


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
