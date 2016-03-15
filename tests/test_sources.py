
from __future__ import absolute_import, division, print_function

import os
import errno
import random
import unittest
from argparse import Namespace
from io import StringIO

from tldptesttools import TestToolsFilesystem

# -- Test Data
import example

# -- SUT
from tldp.sources import SourceCollection, SourceDocument
from tldp.sources import scansourcedirs, sourcedoc_fromdir
from tldp.sources import arg_issourcedoc

sampledocs = os.path.join(os.path.dirname(__file__), 'sample-documents')


class TestFileSourceCollectionMultiDir(TestToolsFilesystem):

    def test_multidir_finding_singlefiles(self):
        ex = random.choice(example.sources)
        doc0 = Namespace(reldir='LDP/howto', stem="A-Unique-Stem")
        doc1 = Namespace(reldir='LDP/guide', stem="A-Different-Stem")
        documents = (doc0, doc1)
        for d in documents:
            d.reldir, d.absdir = self.adddir(d.reldir)
            _, _ = self.addfile(d.reldir, ex.filename, stem=d.stem)
        s = scansourcedirs([x.absdir for x in documents])
        self.assertEqual(2, len(s))
        expected = set([x.stem for x in documents])
        found = set(s.keys())
        self.assertEqual(expected, found)

    def test_multidir_finding_namecollision(self):
        ex = random.choice(example.sources)
        doc0 = Namespace(reldir='LDP/howto', stem="A-Non-Unique-Stem")
        doc1 = Namespace(reldir='LDP/guide', stem="A-Non-Unique-Stem")
        documents = (doc0, doc1)
        for d in documents:
            d.reldir, d.absdir = self.adddir(d.reldir)
            _, _ = self.addfile(d.reldir, ex.filename, stem=d.stem)
        s = scansourcedirs([x.absdir for x in documents])
        self.assertEqual(1, len(s))
        expected = set([x.stem for x in documents])
        found = set(s.keys())
        self.assertEqual(expected, found)


class TestFileSourceCollectionOneDir(TestToolsFilesystem):

    def test_finding_nonfile(self):
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        os.mkfifo(os.path.join(absdir, 'non-dir-non-file.xml'))
        s = scansourcedirs([absdir])
        self.assertEqual(0, len(s))

    def test_finding_singlefile(self):
        ex = random.choice(example.sources)
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        _, _ = self.addfile(reldir, ex.filename)
        s = scansourcedirs([absdir])
        self.assertEqual(1, len(s))

    def test_skipping_misnamed_singlefile(self):
        ex = random.choice(example.sources)
        maindir = 'LDP/LDP/howto'
        reldir, absdir = self.adddir(maindir)
        self.addfile(reldir, ex.filename, ext=".mis")
        s = scansourcedirs([absdir])
        self.assertEqual(1, len(s))

    def test_multiple_stems_of_different_extensions(self):
        ex = random.choice(example.sources)
        stem = 'A-Non-Unique-Stem'
        maindir = os.path.join('LDP/LDP/howto', stem)
        reldir, absdir = self.adddir(maindir)
        self.addfile(reldir, ex.filename, stem=stem, ext=".xml")
        self.addfile(reldir, ex.filename, stem=stem, ext=".md")
        s = scansourcedirs([absdir])
        self.assertEqual(1, len(s))


class TestNullSourceCollection(TestToolsFilesystem):

    def test_SourceCollection_no_dirnames(self):
        s = SourceCollection()
        self.assertIsInstance(s, SourceCollection)
        self.assertTrue('docs' in str(s))


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
        self.assertEqual(0, len(s))


class Test_sourcedoc_fromdir(unittest.TestCase):

    def test_sourcedoc_fromdir_missingdir(self):
        dirname = os.path.dirname('/frobnitz/path/to/extremely/unlikely/file')
        self.assertIsNone(sourcedoc_fromdir(dirname))

    def test_sourcedoc_fromdir_withdots(self):
        dirname = os.path.dirname(example.ex_docbook4xml_dir.filename)
        doc = sourcedoc_fromdir(dirname)
        self.assertIsNotNone(doc)


class Test_arg_issourcedoc(unittest.TestCase):

    def test_arg_issourcedoc_fromdir(self):
        fname = example.ex_linuxdoc_dir.filename
        dirname = os.path.dirname(fname)
        self.assertTrue(fname, arg_issourcedoc(dirname))


class TestSourceDocument(TestToolsFilesystem):

    def test_init(self):
        for ex in example.sources:
            fullpath = ex.filename
            fn = os.path.basename(fullpath)
            doc = SourceDocument(fullpath)
            self.assertIsInstance(doc, SourceDocument)
            self.assertTrue(fn in str(doc))
            self.assertTrue(fn in doc.statinfo)

    def test_fromfifo_should_fail(self):
        fifo = os.path.join(self.tempdir, 'fifofile')
        os.mkfifo(fifo)
        with self.assertRaises(ValueError) as ecm:
            SourceDocument(fifo)
        e = ecm.exception
        self.assertTrue('not identifiable' in e.message)

    def test_fromdir(self):
        dirname = os.path.dirname(example.ex_linuxdoc_dir.filename)
        doc = SourceDocument(dirname)
        self.assertIsInstance(doc, SourceDocument)

    def test_detail(self):
        ex = example.ex_linuxdoc_dir
        s = SourceDocument(ex.filename)
        fout = StringIO()
        widths = Namespace(status=20, doctype=20, stem=50)
        s.detail(widths, False, file=fout)
        fout.seek(0)
        result = fout.read()
        fout.close()
        self.assertTrue(ex.stem in result)
        self.assertTrue('source' in result)

    def test_bad_dir_multiple_doctypes(self):
        fullpath = os.path.join(sampledocs, 'Bad-Dir-Multiple-Doctypes')
        with self.assertRaises(Exception) as ecm:
            SourceDocument(fullpath)
        e = ecm.exception
        self.assertTrue('multiple document choices' in e.message)


class TestMissingSourceDocuments(TestToolsFilesystem):

    def test_init_missing(self):
        missing = os.path.join(self.tempdir, 'vanishing')
        with self.assertRaises(IOError) as ecm:
            SourceDocument(missing)
        e = ecm.exception
        self.assertEqual(errno.ENOENT, e.errno)

    def test_init_wrongtype(self):
        with self.assertRaises(ValueError) as ecm:
            SourceDocument(self.tempdir)
        e = ecm.exception
        self.assertTrue('not identifiable' in e.message)

#
# -- end of file
