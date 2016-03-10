
from __future__ import absolute_import, division, print_function

import os
import uuid
import errno
import random
import unittest
from tempfile import NamedTemporaryFile as ntf
from cStringIO import StringIO
from argparse import Namespace

from tldptesttools import TestInventoryBase, TestToolsFilesystem
from tldp.typeguesser import knowndoctypes
from tldp.inventory import stypes, status_types
from tldp.sources import SourceDocument
from tldp.outputs import OutputDirectory

# -- Test Data
import example

# -- SUT
import tldp.config
import tldp.driver

# -- variables
opj = os.path.join
opd = os.path.dirname
opa = os.path.abspath

sampledocs = opj(opd(__file__), 'sample-documents')

widths = Namespace(status=20, stem=50)


class TestDriverDetail(TestInventoryBase):

    def test_stale_detail_verbosity(self):
        c = self.config
        self.add_stale('Stale-HOWTO', example.ex_docbook4xml)
        c.verbose = True,
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        stdout = StringIO()
        tldp.driver.detail(c, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('newer source' in stdout.read())

    def test_broken_detail_verbosity(self):
        c = self.config
        self.add_broken('Broken-HOWTO', example.ex_docbook4xml)
        c.verbose = True,
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        stdout = StringIO()
        tldp.driver.detail(c, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('missing output' in stdout.read())

    def test_orphan_verbosity(self):
        c = self.config
        self.add_orphan('Orphan-HOWTO', example.ex_docbook4xml)
        c.verbose = True,
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        stdout = StringIO()
        tldp.driver.detail(c, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('missing source' in stdout.read())

    def test_run_detail(self):
        c = self.config
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        self.add_stale('Stale-HOWTO', example.ex_linuxdoc)
        self.add_orphan('Orphan-HOWTO', example.ex_linuxdoc)
        self.add_broken('Broken-HOWTO', example.ex_linuxdoc)
        argv = self.argv
        argv.append('--detail')
        exitcode = tldp.driver.run(argv)
        self.assertEquals(exitcode, os.EX_OK)


class TestDriverShowDoctypes(TestToolsFilesystem):

    def test_show_doctypes(self):
        f = ntf(dir=self.tempdir, prefix='doctypes-', delete=False)
        result = tldp.driver.show_doctypes(Namespace(), file=f)
        self.assertEquals(result, os.EX_OK)
        f.close()
        with open(f.name) as x:
            stdout = x.read()
        for doctype in knowndoctypes:
            self.assertTrue(doctype.formatname in stdout)

    def test_show_doctypes_extraargs(self):
        result = tldp.driver.show_doctypes(Namespace(), 'bogus')
        self.assertTrue('Extra arguments' in result)

    def test_run_doctypes(self):
        exitcode = tldp.driver.run(['--doctypes'])
        self.assertEquals(exitcode, os.EX_OK)


class TestDriverShowStatustypes(TestToolsFilesystem):

    def test_show_statustypes(self):
        stdout = StringIO()
        result = tldp.driver.show_statustypes(Namespace(), file=stdout)
        self.assertEquals(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        for status in status_types:
            self.assertTrue(stypes[status] in data)

    def test_show_statustypes_extraargs(self):
        result = tldp.driver.show_statustypes(Namespace(), 'bogus')
        self.assertTrue('Extra arguments' in result)

    def test_run_statustypes(self):
        exitcode = tldp.driver.run(['--statustypes'])
        self.assertEquals(exitcode, os.EX_OK)


class TestDriverSummary(TestInventoryBase):

    def test_run_summary(self):
        c = self.config
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        self.add_stale('Stale-HOWTO', example.ex_linuxdoc)
        self.add_orphan('Orphan-HOWTO', example.ex_linuxdoc)
        self.add_broken('Broken-HOWTO', example.ex_linuxdoc)
        argv = self.argv
        argv.append('--summary')
        exitcode = tldp.driver.run(argv)
        self.assertEquals(exitcode, os.EX_OK)

    def test_summary_extraargs(self):
        result = tldp.driver.summary(Namespace(), 'bogus')
        self.assertTrue('Extra arguments' in result)

    def test_summary_pubdir(self):
        self.config.pubdir = None
        result = tldp.driver.summary(self.config)
        self.assertTrue('Option --pubdir' in result)

    def test_summary_sourcedir(self):
        self.config.sourcedir = None
        result = tldp.driver.summary(self.config)
        self.assertTrue('Option --sourcedir' in result)

    def publishDocumentsWithLongNames(self, count):
        names = list()
        for _ in range(count):
            x = str(uuid.uuid4())
            names.append(x)
            self.add_published(x, random.choice(example.sources))
        return names

    def test_summary_longnames(self):
        c = self.config
        names = self.publishDocumentsWithLongNames(5)
        stdout = StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEquals(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue('and 4 more' in data)
        c.verbose = True
        stdout = StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEquals(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        for name in names:
            self.assertTrue(name in data)

    def publishDocumentsWithShortNames(self, count):
        names = list()
        for _ in range(count):
            x = hex(random.randint(0, 2**32))
            names.append(x)
            self.add_published(x, random.choice(example.sources))
        return names

    def test_summary_short(self):
        c = self.config
        names = self.publishDocumentsWithShortNames(20)
        stdout = StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEquals(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue('and 16 more' in data)
        c.verbose = True
        stdout = StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEquals(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        for name in names:
            self.assertTrue(name in data)


class TestcreateBuildDirectory(TestToolsFilesystem):

    def test_createBuildDirectory(self):
        d = os.path.join(self.tempdir, 'child', 'grandchild')
        ready, error = tldp.driver.createBuildDirectory(d)
        self.assertFalse(ready)
        self.assertEquals(error, errno.ENOENT)


class Testbuilddir_setup(TestToolsFilesystem):

    def test_builddir_setup_default(self):
        config = Namespace()
        _, config.pubdir = self.adddir('pubdir')
        config.builddir = None
        ready, error = tldp.driver.builddir_setup(config)
        self.assertTrue(ready)

    def test_builddir_setup_specified(self):
        config = Namespace()
        _, config.pubdir = self.adddir('pubdir')
        _, config.builddir = self.adddir('builddir')
        ready, error = tldp.driver.builddir_setup(config)
        self.assertTrue(ready)

class TestremoveUnknownDoctypes(TestToolsFilesystem):

    def test_removeUnknownDoctypes(self):
        docs = list()
        docs.append(SourceDocument(opj(sampledocs, 'Unknown-Doctype.xqf')))
        docs.append(SourceDocument(opj(sampledocs, 'linuxdoc-simple.sgml')))
        result = tldp.driver.removeUnknownDoctypes(docs)
        self.assertEqual(1, len(result))


class Test_prepare_docs_script_mode(TestToolsFilesystem):

    def test_prepare_docs_script_mode_basic(self):
        config = Namespace(pubdir=self.tempdir)
        doc = SourceDocument(opj(sampledocs, 'linuxdoc-simple.sgml'))
        self.assertIsNone(doc.working)
        tldp.driver.prepare_docs_script_mode(config, [doc])
        self.assertIsInstance(doc.working, OutputDirectory)

    def test_prepare_docs_script_mode_existing_output(self):
        config = Namespace(pubdir=self.tempdir)
        doc = SourceDocument(opj(sampledocs, 'linuxdoc-simple.sgml'))
        doc.output = OutputDirectory.fromsource(config.pubdir, doc)
        self.assertIsNone(doc.working)
        tldp.driver.prepare_docs_script_mode(config, [doc])
        self.assertIs(doc.working, doc.output)


class Test_prepare_docs_build_mode(TestInventoryBase):

    def test_prepare_docs_build_mode(self):
        c = self.config
        doc = SourceDocument(opj(sampledocs, 'linuxdoc-simple.sgml'))
        self.assertIsNone(doc.working)
        tldp.driver.prepare_docs_build_mode(c, [doc])
        self.assertIsInstance(doc.working, OutputDirectory)

    def test_prepare_docs_build_mode_nobuilddir(self):
        c = self.config
        os.rmdir(c.builddir)
        doc = SourceDocument(opj(sampledocs, 'linuxdoc-simple.sgml'))
        ready, error = tldp.driver.prepare_docs_build_mode(c, [doc])
        self.assertFalse(ready)


class Test_post_publish_cleanup(TestInventoryBase):

    def test_post_publish_cleanup_enotempty(self):
        c = self.config
        doc = SourceDocument(opj(sampledocs, 'linuxdoc-simple.sgml'))
        tldp.driver.prepare_docs_build_mode(c, [doc])
        with open(opj(doc.dtworkingdir, 'annoyance-file.txt'), 'w'):
            pass
        tldp.driver.post_publish_cleanup([doc])
        self.assertTrue(os.path.isdir(doc.dtworkingdir))


class TestDriverRun(TestInventoryBase):

    def test_run(self):
        c = self.config
        ex = example.ex_linuxdoc
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        self.add_stale('Stale-HOWTO', ex)
        self.add_orphan('Orphan-HOWTO', ex)
        self.add_broken('Broken-HOWTO', ex)
        fullpath = opj(self.tempdir, 'sources', 'New-HOWTO.sgml')
        argv = self.argv
        argv.extend(['--publish', 'stale', 'Orphan-HOWTO', fullpath])
        exitcode = tldp.driver.run(argv)
        self.assertEquals(exitcode, os.EX_OK)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(4, len(inv.published.keys()))
        self.assertEquals(1, len(inv.broken.keys()))

    def test_run_no_work(self):
        c = self.config
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        exitcode = tldp.driver.run(self.argv)
        # -- improvement: check for 'No work to do.' from logger
        self.assertEquals(exitcode, os.EX_OK)

    def test_run_loglevel_resetting(self):
        '''just exercise the loglevel settings'''
        argv = ['--doctypes', '--loglevel', 'debug']
        tldp.driver.run(argv)

    def test_run_extra_args(self):
        c = self.config
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        fullpath = opj(self.tempdir, 'sources', 'New-HOWTO.sgml')
        argv = self.argv
        argv.extend(['--build', 'stale', 'Orphan-HOWTO', fullpath, 'extra'])
        val = tldp.driver.run(argv)
        self.assertTrue('Unknown arguments' in val)

    def test_run_no_action(self):
        c = self.config
        ex = example.ex_linuxdoc
        self.add_new('New-HOWTO', ex)
        tldp.driver.run(self.argv)
        docbuilddir = opj(c.builddir, ex.doctype.__name__)
        inv = tldp.inventory.Inventory(docbuilddir, c.sourcedir)
        self.assertEquals(1, len(inv.published.keys()))

    def test_run_oops_no_sourcedir(self):
        c = self.config
        argv = ['--pubdir', c.pubdir]
        ex = example.ex_linuxdoc
        self.add_new('New-HOWTO', ex)
        exitcode = tldp.driver.run(argv)
        self.assertTrue('required for inventory' in exitcode)

    def test_run_oops_no_pubdir(self):
        c = self.config
        argv = ['--sourcedir', c.sourcedir[0]]
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        exitcode = tldp.driver.run(argv)
        self.assertTrue('required for inventory' in exitcode)

    def test_run_build_no_pubdir(self):
        c = self.config
        argv = ['--sourcedir', c.sourcedir[0]]
        fname = opj(sampledocs, 'linuxdoc-simple.sgml')
        argv.append(fname)
        exitcode = tldp.driver.run(argv)
        self.assertTrue('to --build' in exitcode)

    def test_run_status_selection(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        c.script = True
        stdout = StringIO()
        self.add_stale('Asciidoc-Stale-HOWTO', example.ex_asciidoc)
        self.add_new('DocBook4XML-New-HOWTO', example.ex_docbook4xml)
        argv = self.argv
        argv.extend(['--publish', 'stale'])
        exitcode = tldp.driver.run(argv)
        self.assertEquals(exitcode, os.EX_OK)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.published.keys()))


class TestDriverProcessSkips(TestInventoryBase):

    def test_skipDocuments_status(self):
        c = self.config
        ex = example.ex_linuxdoc
        self.add_new('New-HOWTO', ex)
        self.add_stale('Stale-HOWTO', ex)
        c.skip = ['stale']
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        inc, exc = tldp.driver.processSkips(c, docs)
        self.assertTrue(1, len(exc))
        excluded = exc.pop()
        self.assertEquals(excluded.stem, 'Stale-HOWTO')
        self.assertEquals(len(inc) + 1, len(inv.all.keys()))

    def test_skipDocuments_stem(self):
        c = self.config
        ex = example.ex_linuxdoc
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        c.skip = ['Published-HOWTO']
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        inc, exc = tldp.driver.processSkips(c, docs)
        self.assertTrue(1, len(exc))
        excluded = exc.pop()
        self.assertEquals(excluded.stem, 'Published-HOWTO')
        self.assertEquals(len(inc) + 1, len(inv.all.keys()))

    def test_skipDocuments_doctype(self):
        c = self.config
        self.add_published('Linuxdoc-HOWTO', example.ex_linuxdoc)
        self.add_new('Docbook4XML-HOWTO', example.ex_docbook4xml)
        c.skip = ['Docbook4XML']
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        inc, exc = tldp.driver.processSkips(c, docs)
        self.assertTrue(1, len(exc))
        excluded = exc.pop()
        self.assertEquals(excluded.stem, 'Docbook4XML-HOWTO')
        self.assertEquals(len(inc) + 1, len(inv.all.keys()))


class TestDriverScript(TestInventoryBase):

    def test_script(self):
        c = self.config
        c.script = True
        stdout = StringIO()
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        tldp.driver.script(c, inv.all.values(), file=stdout)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue(c.linuxdoc_sgml2html in data)

    def test_run_script(self):
        c = self.config
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        self.add_stale('Stale-HOWTO', example.ex_linuxdoc)
        self.add_orphan('Orphan-HOWTO', example.ex_linuxdoc)
        self.add_broken('Broken-HOWTO', example.ex_linuxdoc)
        argv = self.argv
        argv.append('--script')
        exitcode = tldp.driver.run(argv)
        self.assertEquals(exitcode, os.EX_OK)


@unittest.skip("Except when you want to spend time....")
class TestDriverBuild(TestInventoryBase):

    def test_build_one_broken(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        c.build = True
        self.add_new('Frobnitz-DocBook-XML-4-HOWTO', example.ex_docbook4xml)
        # -- mangle the content of a valid DocBook XML file
        borked = example.ex_docbook4xml.content[:-12]
        self.add_new('Frobnitz-Borked-XML-4-HOWTO',
                     example.ex_docbook4xml, content=borked)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(2, len(inv.all.keys()))
        docs = inv.all.values()
        result = tldp.driver.build(c, docs)
        self.assertTrue('Build failed' in result)

    def test_build_only_requested_stem(self):
        c = self.config
        ex = example.ex_linuxdoc
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        argv = ['--pubdir', c.pubdir, '--sourcedir', c.sourcedir[0]]
        argv.extend(['--build', 'Published-HOWTO'])
        tldp.driver.run(argv)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.published.keys()))
        self.assertEquals(1, len(inv.work.keys()))



@unittest.skip("Except when you want to spend time....")
class TestDriverPublish(TestInventoryBase):

    def test_publish_docbook4xml(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-DocBook-XML-4-HOWTO', example.ex_docbook4xml)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

    def test_publish_asciidoc(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-Asciidoc-HOWTO', example.ex_asciidoc)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        c.skip = []
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

    def test_publish_linuxdoc(self):
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-Linuxdoc-HOWTO', example.ex_linuxdoc)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        c.skip = []
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

    def test_publish_docbooksgml(self):
        self.add_docbooksgml_support_to_config()
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-DocBookSGML-HOWTO', example.ex_docbooksgml)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

#
# -- end of file
