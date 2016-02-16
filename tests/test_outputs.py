
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

# -- Test Data
import examples

# -- SUT
from tldp.outputs import OutputCollection, OutputDirectory

datadir = os.path.join(os.path.dirname(__file__), 'testdata')


def stem_and_ext(name):
    stem, ext = os.path.splitext(os.path.basename(name))
    assert ext != ''
    return stem, ext


class TestOutputCollection(unittest.TestCase):

    def setUp(self):
        self.tempdir = mkdtemp(prefix='tldp-outputs-test-')

    def tearDown(self):
        shutil.rmtree(self.tempdir)


class TestMissingOutputCollection(TestOutputCollection):

    def test_not_a_directory(self):
        missing = os.path.join(self.tempdir, 'vanishing')
        with self.assertRaises(IOError) as ecm:
            OutputCollection(missing)
        e = ecm.exception
        self.assertEquals(errno.ENOENT, e.errno)

#
# -- end of file
