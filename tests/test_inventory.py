
from __future__ import absolute_import, division, print_function

import os
import time
import random
import shutil

from tldp.outputs import OutputNamingConvention
from tldptesttools import TestToolsFilesystem

# -- Test Data
import example

# -- SUT
from tldp.inventory import Inventory

datadir = os.path.join(os.path.dirname(__file__), 'testdata')


class TestOutputDirSkeleton(OutputNamingConvention):

    def mkdir(self):
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname)

    def create_expected_docs(self):
        for name in self.expected:
            fname = getattr(self, name)
            with open(fname, 'w'):
                pass


class TestSourceDocSkeleton(object):

    def __init__(self, dirname):
        if not os.path.abspath(dirname):
            raise Exception("Please use absolute path in unit tests....")
        self.dirname = dirname
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname)

    def addsourcefile(self, filename, content):
        fname = os.path.join(self.dirname, filename)
        if os.path.isfile(content):
            shutil.copy(content, fname)
        else:
            with open(fname, 'w') as f:
                f.write(content)


class TestInventoryBase(TestToolsFilesystem):

    def setupcollections(self):
        self.pubdir = os.path.join(self.tempdir, 'outputs')
        self.sourcedir = os.path.join(self.tempdir, 'sources')
        self.sourcedirs = [self.sourcedir]
        for d in (self.sourcedir, self.pubdir):
            if not os.path.isdir(d):
                os.mkdir(d)

    def add_stale(self, stem, ex):
        self.setupcollections()
        myoutput = TestOutputDirSkeleton(os.path.join(self.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()
        time.sleep(0.002)
        mysource = TestSourceDocSkeleton(self.sourcedir)
        mysource.addsourcefile(stem + ex.ext, ex.filename)

    def add_broken(self, stem, ex):
        self.setupcollections()
        mysource = TestSourceDocSkeleton(self.sourcedir)
        mysource.addsourcefile(stem + ex.ext, ex.filename)
        myoutput = TestOutputDirSkeleton(os.path.join(self.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()
        prop = random.choice(myoutput.expected)
        fname = getattr(myoutput, prop, None)
        assert fname is not None
        os.unlink(fname)

    def add_new(self, stem, ex):
        self.setupcollections()
        mysource = TestSourceDocSkeleton(self.sourcedir)
        mysource.addsourcefile(stem + ex.ext, ex.filename)

    def add_orphan(self, stem, ex):
        self.setupcollections()
        myoutput = TestOutputDirSkeleton(os.path.join(self.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()

    def add_published(self, stem, ex):
        self.setupcollections()
        mysource = TestSourceDocSkeleton(self.sourcedir)
        mysource.addsourcefile(stem + ex.ext, ex.filename)
        myoutput = TestOutputDirSkeleton(os.path.join(self.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()


class TestInventoryUsage(TestInventoryBase):

    def test_inventory_repr(self):
        ex = random.choice(example.sources)
        self.add_published('Frobnitz-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertTrue('1 published' in str(i))

    def test_detect_status_published(self):
        ex = random.choice(example.sources)
        self.add_published('Frobnitz-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertEquals(0, len(i.stale))
        self.assertEquals(1, len(i.published))
        self.assertEquals(0, len(i.new))
        self.assertEquals(0, len(i.orphan))
        self.assertEquals(0, len(i.broken))

    def test_detect_status_new(self):
        ex = random.choice(example.sources)
        self.add_new('Frobnitz-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertEquals(0, len(i.stale))
        self.assertEquals(0, len(i.published))
        self.assertEquals(1, len(i.new))
        self.assertEquals(0, len(i.orphan))
        self.assertEquals(0, len(i.broken))

    def test_detect_status_orphan(self):
        ex = random.choice(example.sources)
        self.add_orphan('Frobnitz-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertEquals(0, len(i.stale))
        self.assertEquals(0, len(i.published))
        self.assertEquals(0, len(i.new))
        self.assertEquals(1, len(i.orphan))
        self.assertEquals(0, len(i.broken))

    def test_detect_status_stale(self):
        ex = random.choice(example.sources)
        self.add_stale('Frobnitz-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertEquals(1, len(i.stale))
        self.assertEquals(1, len(i.published))
        self.assertEquals(0, len(i.new))
        self.assertEquals(0, len(i.orphan))
        self.assertEquals(0, len(i.broken))

    def test_detect_status_broken(self):
        ex = random.choice(example.sources)
        self.add_broken('Frobnitz-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertEquals(0, len(i.stale))
        self.assertEquals(1, len(i.published))
        self.assertEquals(0, len(i.new))
        self.assertEquals(0, len(i.orphan))
        self.assertEquals(1, len(i.broken))

#
# -- end of file
