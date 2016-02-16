
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

from tldptesttools import *

# -- Test Data
import examples

# -- SUT
from tldp.outputs import OutputCollection
from tldp.outputs import OutputDirectory
from tldp.outputs import OutputNamingConvention

datadir = os.path.join(os.path.dirname(__file__), 'testdata')


def stem_and_ext(name):
    stem, ext = os.path.splitext(os.path.basename(name))
    assert ext != ''
    return stem, ext


class TestOutputNamingConvention(unittest.TestCase):

    def test_namesets(self):
        onc = OutputNamingConvention("Stem", "/path/to/output/")
        self.assertTrue(onc.name_txt.endswith(".txt"))
        self.assertTrue(onc.name_pdf.endswith(".pdf"))
        self.assertTrue(onc.name_html.endswith(".html"))
        self.assertTrue(onc.name_htmls.endswith("-single.html"))
        self.assertTrue(onc.name_index.endswith("index.html"))


class TestMissingOutputCollection(TestToolsFilesystem):

    def test_not_a_directory(self):
        missing = os.path.join(self.tempdir, 'vanishing')
        with self.assertRaises(IOError) as ecm:
            OutputCollection(missing)
        e = ecm.exception
        self.assertEquals(errno.ENOENT, e.errno)

#
# -- end of file
