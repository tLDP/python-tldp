
from __future__ import absolute_import, division, print_function

import os
from cStringIO import StringIO
from argparse import Namespace

from tldptesttools import TestInventoryBase

# -- Test Data
import example

# -- SUT
import tldp.config
import tldp.driver

widths = Namespace(status=20, stem=50)


class TestDriverDetail(TestInventoryBase):

    def test_stale_detail_verbosity(self):
        self.add_stale('Frobnitz-HOWTO', example.ex_docbook4xml)
        config = Namespace(
                           pubdir=self.pubdir,
                           sourcedir=self.sourcedirs,
                           verbose=True,
                           )
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
        docs = inv.all.values()
        stdout = StringIO()
        tldp.driver.detail(config, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('newer file' in stdout.read())

    def test_broken_detail_verbosity(self):
        self.add_broken('Frobnitz-HOWTO', example.ex_docbook4xml)
        config = Namespace(
                           pubdir=self.pubdir,
                           sourcedir=self.sourcedirs,
                           verbose=True,
                           )
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
        docs = inv.all.values()
        stdout = StringIO()
        tldp.driver.detail(config, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('missing file' in stdout.read())


class TestDriverBuild(TestInventoryBase):

    def test_build_linuxdoc(self):
        self.add_new('Frobnitz-Linuxdoc-HOWTO', example.ex_linuxdoc)
        config, args = tldp.config.collectconfiguration('ldptool', [])
        config.pubdir = self.pubdir
        config.sourcedir = self.sourcedirs
        config.skip = []
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        tldp.driver.build(config, docs)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

    def test_build_docbooksgml(self):
        self.add_new('Frobnitz-DocBook-SGML-HOWTO', example.ex_docbooksgml)
        config, args = tldp.config.collectconfiguration('ldptool', [])
        config.pubdir = self.pubdir
        config.sourcedir = self.sourcedirs
        config.skip = ['Frobnitz-DocBook-SGML-HOWTO']
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        tldp.driver.build(config, docs)
        doc = docs.pop(0)
        self.assertFalse(doc.output.iscomplete)
        # -- after figuring out collateindex and friends, this should say
        # self.assertTrue(doc.output.iscomplete)

    def test_build_docbook4xml(self):
        self.add_new('Frobnitz-DocBook-XML-4-HOWTO', example.ex_docbook4xml)
        config, args = tldp.config.collectconfiguration('ldptool', [])
        config.pubdir = self.pubdir
        config.sourcedir = self.sourcedirs
        config.skip = ['Frobnitz-DocBook-XML-4-HOWTO']
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        tldp.driver.build(config, docs)
        doc = docs.pop(0)
        self.assertFalse(doc.output.iscomplete)
        # -- after figuring out the XSL files at test time, this should say
        # self.assertTrue(doc.output.iscomplete)


class TestDriverSummary(TestInventoryBase):

    def test_summary(self):
        self.add_new('Frobnitz-DocBook-XML-4-HOWTO', example.ex_docbook4xml)
        config, args = tldp.config.collectconfiguration('ldptool', [])
        config.pubdir = self.pubdir
        config.sourcedir = self.sourcedirs
        stdout = StringIO()
        tldp.driver.summary(config, None, file=stdout)
        stdout.seek(0)
        parts = stdout.read().split()
        idx = parts.index('new')
        self.assertEqual(['new', '1'], parts[idx:idx+2])


class TestDriverRun(TestInventoryBase):

    def test_run(self):
        ex = example.ex_linuxdoc
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        self.add_stale('Stale-HOWTO', ex)
        self.add_orphan('Orphan-HOWTO', ex)
        self.add_broken('Broken-HOWTO', ex)
        argv = ['--pubdir', self.pubdir, '--sourcedir', self.sourcedir]
        fullpath = os.path.join(self.tempdir, 'sources', 'Published-HOWTO.sgml')
        argv.extend(['stale', 'Orphan-HOWTO', fullpath])
        tldp.driver.run(argv)
        inv = tldp.inventory.Inventory(self.pubdir, self.sourcedirs)
        self.assertEquals(3, len(inv.published.keys()))

    def test_run_no_action(self):
        ex = example.ex_linuxdoc
        self.add_new('New-HOWTO', ex)
        argv = ['--pubdir', self.pubdir, '--sourcedir', self.sourcedir]
        tldp.driver.run(argv)
        inv = tldp.inventory.Inventory(self.pubdir, self.sourcedirs)
        self.assertEquals(1, len(inv.published.keys()))

    def test_run_oops_no_sourcedir(self):
        ex = example.ex_linuxdoc
        self.add_new('New-HOWTO', ex)
        argv = ['--pubdir', self.pubdir]
        exit = tldp.driver.run(argv)
        self.assertTrue('required for inventory' in exit)

    def test_run_oops_no_pubdir(self):
        ex = example.ex_linuxdoc
        self.add_new('New-HOWTO', ex)
        argv = ['--sourcedir', self.sourcedir]
        exit = tldp.driver.run(argv)
        self.assertTrue('required for inventory' in exit)


class TestDriverProcessSkips(TestInventoryBase):

    def test_skipDocuments_status(self):
        ex = example.ex_linuxdoc
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        self.add_stale('Stale-HOWTO', ex)
        self.add_orphan('Orphan-HOWTO', ex)
        self.add_broken('Broken-HOWTO', ex)
        config, args = tldp.config.collectconfiguration('ldptool', [])
        config.pubdir = self.pubdir
        config.sourcedir = self.sourcedirs
        config.skip = ['stale']
        inv = tldp.inventory.Inventory(self.pubdir, self.sourcedirs)
        docs = inv.all.values()
        inc, exc = tldp.driver.processSkips(config, docs)
        self.assertTrue(1, len(exc))
        excluded = exc.pop()
        self.assertEquals(excluded.stem, 'Stale-HOWTO')
        self.assertEquals(len(inc) + 1, len(inv.all.keys()))

    def test_skipDocuments_stem(self):
        ex = example.ex_linuxdoc
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        self.add_stale('Stale-HOWTO', ex)
        self.add_orphan('Orphan-HOWTO', ex)
        self.add_broken('Broken-HOWTO', ex)
        config, args = tldp.config.collectconfiguration('ldptool', [])
        config.pubdir = self.pubdir
        config.sourcedir = self.sourcedirs
        config.skip = ['Published-HOWTO']
        inv = tldp.inventory.Inventory(self.pubdir, self.sourcedirs)
        docs = inv.all.values()
        inc, exc = tldp.driver.processSkips(config, docs)
        self.assertTrue(1, len(exc))
        excluded = exc.pop()
        self.assertEquals(excluded.stem, 'Published-HOWTO')
        self.assertEquals(len(inc) + 1, len(inv.all.keys()))

    def test_skipDocuments_doctype(self):
        self.add_published('Linuxdoc-HOWTO', example.ex_linuxdoc)
        self.add_new('Docbook4XML-HOWTO', example.ex_docbook4xml)
        config, args = tldp.config.collectconfiguration('ldptool', [])
        config.pubdir = self.pubdir
        config.sourcedir = self.sourcedirs
        config.skip = ['Docbook4XML']
        inv = tldp.inventory.Inventory(self.pubdir, self.sourcedirs)
        docs = inv.all.values()
        inc, exc = tldp.driver.processSkips(config, docs)
        self.assertTrue(1, len(exc))
        excluded = exc.pop()
        self.assertEquals(excluded.stem, 'Docbook4XML-HOWTO')
        self.assertEquals(len(inc) + 1, len(inv.all.keys()))

#
# -- end of file
