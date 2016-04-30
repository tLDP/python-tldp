# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function

import io
import os
import codecs
import shutil

from tldptesttools import TestInventoryBase, TestSourceDocSkeleton

# -- Test Data
import example

# -- SUT
import tldp.driver

opb = os.path.basename
opj = os.path.join


class TestInventoryHandling(TestInventoryBase):

    def test_lifecycle(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        argv = self.argv
        argv.extend(['--publish'])
        argv.extend(['--docbook4xml-xslprint', c.docbook4xml_xslprint])
        argv.extend(['--docbook4xml-xslchunk', c.docbook4xml_xslchunk])
        argv.extend(['--docbook4xml-xslsingle', c.docbook4xml_xslsingle])
        mysource = TestSourceDocSkeleton(c.sourcedir)
        ex = example.ex_docbook4xml_dir
        exdir = os.path.dirname(ex.filename)
        mysource.copytree(exdir)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(1, len(inv.new.keys()))

        # -- run first build (will generate MD5SUMS file
        #
        exitcode = tldp.driver.run(argv)
        self.assertEqual(exitcode, os.EX_OK)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(1, len(inv.published.keys()))

        # -- remove the generated MD5SUMS file, ensure rebuild occurs
        #
        doc = inv.published.values().pop()
        os.unlink(doc.output.MD5SUMS)
        self.assertEqual(dict(), doc.output.md5sums)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(1, len(inv.stale.keys()))
        if not os.path.isdir(c.builddir):
            os.mkdir(c.builddir)
        exitcode = tldp.driver.run(argv)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(1, len(inv.published.keys()))

        # -- remove a source file, add a source file, change a source file
        #
        main = opj(mysource.dirname, opb(exdir), opb(ex.filename))
        disappearing = opj(mysource.dirname, opb(exdir), 'disappearing.xml')
        brandnew = opj(mysource.dirname, opb(exdir), 'brandnew.xml')
        shutil.copy(disappearing, brandnew)
        os.unlink(opj(mysource.dirname, opb(exdir), 'disappearing.xml'))
        with codecs.open(main, 'w', encoding='utf-8') as f:
            f.write(ex.content.replace('FIXME', 'TOTALLY-FIXED'))
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(1, len(inv.stale.keys()))
        stdout = io.StringIO()
        c.verbose = True
        tldp.driver.detail(c, inv.all.values(), file=stdout)
        stdout.seek(0)
        data = stdout.read()
        self.assertTrue('new source' in data)
        self.assertTrue('gone source' in data)
        self.assertTrue('changed source' in data)

        # -- rebuild (why not?)
        #
        if not os.path.isdir(c.builddir):
            os.mkdir(c.builddir)
        exitcode = tldp.driver.run(argv)
        self.assertEqual(exitcode, os.EX_OK)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(1, len(inv.published.keys()))

        # -- remove a file (known extraneous file, build should succeed)

#
# -- end of file
