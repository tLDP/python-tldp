# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals


import random

from tldptesttools import TestInventoryBase

# -- Test Data
import example

# -- SUT
from tldp.inventory import Inventory


class TestInventoryUsage(TestInventoryBase):

    def test_inventory_repr(self):
        c = self.config
        ex = random.choice(example.sources)
        self.add_published('Frobnitz-HOWTO', ex)
        i = Inventory(c.pubdir, c.sourcedir)
        self.assertTrue('1 published' in str(i))

    def test_status_class_accessors(self):
        c = self.config
        ex = random.choice(example.sources)
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        self.add_stale('Stale-HOWTO', ex)
        self.add_orphan('Orphan-HOWTO', ex)
        self.add_broken('Broken-HOWTO', ex)
        i = Inventory(c.pubdir, c.sourcedir)
        self.assertTrue('Orphan-HOWTO' in i.orphans.keys())
        self.assertTrue('Orphan-HOWTO' in i.orphaned.keys())
        self.assertTrue(3, len(i.problems.keys()))
        self.assertTrue(4, len(i.work.keys()))
        self.assertTrue(5, len(i.all.keys()))
        self.assertTrue(5, len(i.sources.keys()))
        self.assertTrue(5, len(i.outputs.keys()))

    def test_detect_status_published(self):
        c = self.config
        ex = random.choice(example.sources)
        self.add_published('Frobnitz-Published-HOWTO', ex)
        i = Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(0, len(i.stale))
        self.assertEqual(1, len(i.published))
        self.assertEqual(0, len(i.new))
        self.assertEqual(0, len(i.orphan))
        self.assertEqual(0, len(i.broken))

    def test_detect_status_new(self):
        c = self.config
        ex = random.choice(example.sources)
        self.add_new('Frobnitz-New-HOWTO', ex)
        i = Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(0, len(i.stale))
        self.assertEqual(0, len(i.published))
        self.assertEqual(1, len(i.new))
        self.assertEqual(0, len(i.orphan))
        self.assertEqual(0, len(i.broken))

    def test_detect_status_orphan(self):
        c = self.config
        ex = random.choice(example.sources)
        self.add_orphan('Frobnitz-Orphan-HOWTO', ex)
        i = Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(0, len(i.stale))
        self.assertEqual(0, len(i.published))
        self.assertEqual(0, len(i.new))
        self.assertEqual(1, len(i.orphan))
        self.assertEqual(0, len(i.broken))

    def test_detect_status_stale(self):
        c = self.config
        ex = random.choice(example.sources)
        self.add_stale('Frobnitz-Stale-HOWTO', ex)
        i = Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(1, len(i.stale))
        self.assertEqual(1, len(i.published))
        self.assertEqual(0, len(i.new))
        self.assertEqual(0, len(i.orphan))
        self.assertEqual(0, len(i.broken))

    def test_detect_status_broken(self):
        c = self.config
        ex = random.choice(example.sources)
        self.add_broken('Frobnitz-Broken-HOWTO', ex)
        i = Inventory(c.pubdir, c.sourcedir)
        self.assertEqual(0, len(i.stale))
        self.assertEqual(1, len(i.published))
        self.assertEqual(0, len(i.new))
        self.assertEqual(0, len(i.orphan))
        self.assertEqual(1, len(i.broken))

#
# -- end of file
