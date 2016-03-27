
from __future__ import absolute_import, division, print_function

import io
import os
import uuid
import errno
import codecs
import random
from tempfile import NamedTemporaryFile as ntf
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
        stdout = io.StringIO()
        tldp.driver.detail(c, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('newer source' in stdout.read())

    def test_broken_detail_verbosity(self):
        c = self.config
        self.add_broken('Broken-HOWTO', example.ex_docbook4xml)
        c.verbose = True,
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        stdout = io.StringIO()
        tldp.driver.detail(c, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('missing output' in stdout.read())

    def test_orphan_verbosity(self):
        c = self.config
        self.add_orphan('Orphan-HOWTO', example.ex_docbook4xml)
        c.verbose = True,
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        docs = inv.all.values()
        stdout = io.StringIO()
        tldp.driver.detail(c, docs, file=stdout)
        stdout.seek(0)
        self.assertTrue('missing source' in stdout.read())

    def test_run_detail(self):
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        self.add_stale('Stale-HOWTO', example.ex_linuxdoc)
        self.add_orphan('Orphan-HOWTO', example.ex_linuxdoc)
        self.add_broken('Broken-HOWTO', example.ex_linuxdoc)
        argv = self.argv
        argv.append('--detail')
        exitcode = tldp.driver.run(argv)
        self.assertEqual(exitcode, os.EX_OK)


class TestDriverShowDoctypes(TestToolsFilesystem):

    def test_show_doctypes(self):
        tf = ntf(dir=self.tempdir, prefix='doctypes-', delete=False)
        tf.close()
        with codecs.open(tf.name, 'w', encoding='utf-8') as f:
            result = tldp.driver.show_doctypes(Namespace(), file=f)
        self.assertEqual(result, os.EX_OK)
        with codecs.open(f.name, encoding='utf-8') as x:
            stdout = x.read()
        for doctype in knowndoctypes:
            self.assertTrue(doctype.formatname in stdout)

    def test_show_doctypes_extraargs(self):
        result = tldp.driver.show_doctypes(Namespace(), 'bogus')
        self.assertTrue('Extra arguments' in result)

    def test_run_doctypes(self):
        exitcode = tldp.driver.run(['--doctypes'])
        self.assertEqual(exitcode, os.EX_OK)


class TestDriverShowStatustypes(TestToolsFilesystem):

    def test_show_statustypes(self):
        stdout = io.StringIO()
        result = tldp.driver.show_statustypes(Namespace(), file=stdout)
        self.assertEqual(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        for status in status_types:
            self.assertTrue(stypes[status] in data)

    def test_show_statustypes_extraargs(self):
        result = tldp.driver.show_statustypes(Namespace(), 'bogus')
        self.assertTrue('Extra arguments' in result)

    def test_run_statustypes(self):
        exitcode = tldp.driver.run(['--statustypes'])
        self.assertEqual(exitcode, os.EX_OK)


class TestDriverSummary(TestInventoryBase):

    def test_run_summary(self):
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        self.add_stale('Stale-HOWTO', example.ex_linuxdoc)
        self.add_orphan('Orphan-HOWTO', example.ex_linuxdoc)
        self.add_broken('Broken-HOWTO', example.ex_linuxdoc)
        argv = self.argv
        argv.append('--summary')
        exitcode = tldp.driver.run(argv)
        self.assertEqual(exitcode, os.EX_OK)

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
        stdout = io.StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEqual(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue('and 4 more' in data)
        c.verbose = True
        stdout = io.StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEqual(result, os.EX_OK)
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
        stdout = io.StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEqual(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue('and 16 more' in data)
        c.verbose = True
        stdout = io.StringIO()
        result = tldp.driver.summary(c, file=stdout)
        self.assertEqual(result, os.EX_OK)
        stdout.seek(0)
        data = stdout.read()
        for name in names:
            self.assertTrue(name in data)


class TestcreateBuildDirectory(TestToolsFilesystem):

    def test_createBuildDirectory(self):
        d = os.path.join(self.tempdir, 'child', 'grandchild')
        ready, error = tldp.driver.createBuildDirectory(d)
        self.assertFalse(ready)
        self.assertEqual(error, errno.ENOENT)


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
        self.assertEqual(exitcode, os.EX_OK)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(4, len(inv.published.keys()))
        self.assertEqual(1, len(inv.broken.keys()))

    def test_run_no_work(self):
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        exitcode = tldp.driver.run(self.argv)
        # -- improvement: check for 'No work to do.' from logger
        self.assertEqual(exitcode, os.EX_OK)

    def test_run_loglevel_resetting(self):
        '''just exercise the loglevel settings'''
        argv = ['--doctypes', '--loglevel', 'debug']
        tldp.driver.run(argv)

    def test_run_extra_args(self):
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
        self.assertEqual(1, len(inv.published.keys()))

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
        self.assertEqual(excluded.stem, 'Stale-HOWTO')
        self.assertEqual(len(inc) + 1, len(inv.all.keys()))

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
        self.assertEqual(excluded.stem, 'Published-HOWTO')
        self.assertEqual(len(inc) + 1, len(inv.all.keys()))

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
        self.assertEqual(excluded.stem, 'Docbook4XML-HOWTO')
        self.assertEqual(len(inc) + 1, len(inv.all.keys()))


class TestDriverScript(TestInventoryBase):

    def test_script(self):
        c = self.config
        c.script = True
        stdout = io.StringIO()
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        tldp.driver.script(c, inv.all.values(), file=stdout)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue('Published-HOWTO' in data)

    def test_script_no_pubdir(self):
        c = self.config
        c.script = True
        stdout = io.StringIO()
        self.add_published('New-HOWTO', example.ex_linuxdoc)
        c.pubdir = None
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        tldp.driver.script(c, inv.all.values(), file=stdout)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue('New-HOWTO' in data)

    def test_run_script(self):
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        self.add_new('New-HOWTO', example.ex_linuxdoc)
        self.add_stale('Stale-HOWTO', example.ex_linuxdoc)
        self.add_orphan('Orphan-HOWTO', example.ex_linuxdoc)
        self.add_broken('Broken-HOWTO', example.ex_linuxdoc)
        argv = self.argv
        argv.append('--script')
        exitcode = tldp.driver.run(argv)
        self.assertEqual(exitcode, os.EX_OK)

    def test_script_bad_invocation(self):
        c = self.config
        c.script = False
        self.add_published('Published-HOWTO', example.ex_linuxdoc)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        with self.assertRaises(Exception) as ecm:
            tldp.driver.script(c, inv.all.values())
        e = ecm.exception
        self.assertTrue("neither --build nor --script" in e.args[0])

#
# -- end of file
