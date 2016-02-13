
from __future__ import absolute_import, division, print_function

import os
import unittest
from tempfile import NamedTemporaryFile as ntf
from tempfile import mkdtemp, mkstemp
import shutil

# -- Test Data
from examples import *

# -- SUT
from tldp.sources import Sources, SourceDocument


class TestSources(unittest.TestCase):

    def setUp(self):
        self.tempdir = mkdtemp(prefix='tldp-sources-test-')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

class TestInvalidSources(TestSources):

    def test_validateDirs_onebad(self):
        invalid0 = os.path.join(self.tempdir, 'unique', 'rabbit')
        with self.assertRaises(OSError) as ecm:
            Sources([invalid0])
        e = ecm.exception
        self.assertTrue('unique/rabbit' in e.message)

    def test_validateDirs_multibad(self):
        invalid0 = os.path.join(self.tempdir, 'unique', 'rabbit')
        invalid1 = os.path.join(self.tempdir, 'affable', 'elephant')
        with self.assertRaises(OSError) as ecm:
            Sources([invalid0, invalid1])
        e = ecm.exception
        self.assertTrue('affable/elephant' in e.message)

    def testEmptyDir(self):
        s = Sources([self.tempdir])
        self.assertEquals(0, len(s.docs))
        

#
# -- end of file
