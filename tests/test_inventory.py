
from __future__ import absolute_import, division, print_function

import random

from tldptesttools import TestInventoryBase

# -- Test Data
import example

# -- SUT
from tldp.inventory import Inventory


class TestInventoryUsage(TestInventoryBase):

    def test_inventory_repr(self):
        ex = random.choice(example.sources)
        self.add_published('Frobnitz-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertTrue('1 published' in str(i))

    def test_status_class_accessors(self):
        ex = random.choice(example.sources)
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        self.add_stale('Stale-HOWTO', ex)
        self.add_orphan('Orphan-HOWTO', ex)
        self.add_broken('Broken-HOWTO', ex)
        i = Inventory(self.pubdir, self.sourcedirs)
        self.assertTrue('Orphan-HOWTO' in i.orphans.keys())
        self.assertTrue('Orphan-HOWTO' in i.orphaned.keys())
        self.assertTrue(3, len(i.problems.keys()))
        self.assertTrue(4, len(i.work.keys()))
        self.assertTrue(5, len(i.all.keys()))
        self.assertTrue(5, len(i.sources.keys()))
        self.assertTrue(5, len(i.outputs.keys()))

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
