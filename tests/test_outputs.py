
from __future__ import absolute_import, division, print_function

import os
import errno
import unittest
import random

from tldptesttools import TestToolsFilesystem

# -- SUT
from tldp.outputs import OutputCollection
from tldp.outputs import OutputDirectory
from tldp.outputs import OutputNamingConvention


class TestOutputNamingConvention(unittest.TestCase):

    def test_namesets(self):
        onc = OutputNamingConvention("/path/to/output/", "Stem")
        self.assertTrue(onc.name_txt.endswith(".txt"))
        self.assertTrue(onc.name_pdf.endswith(".pdf"))
        self.assertTrue(onc.name_epub.endswith(".epub"))
        self.assertTrue(onc.name_html.endswith(".html"))
        self.assertTrue(onc.name_htmls.endswith("-single.html"))
        self.assertTrue(onc.name_indexhtml.endswith("index.html"))


class TestOutputCollection(TestToolsFilesystem):

    def test_not_a_directory(self):
        missing = os.path.join(self.tempdir, 'vanishing')
        with self.assertRaises(IOError) as ecm:
            OutputCollection(missing)
        e = ecm.exception
        self.assertEquals(errno.ENOENT, e.errno)

    def test_file_in_output_collection(self):
        reldir, absdir = self.adddir('collection')
        self.addfile('collection', __file__,  stem='non-directory')
        oc = OutputCollection(absdir)
        self.assertEquals(0, len(oc))

    def test_manyfiles(self):
        reldir, absdir = self.adddir('manyfiles')
        count = random.randint(8, 15)
        for x in range(count):
            self.adddir('manyfiles/Document-Stem-' + str(x))
        oc = OutputCollection(absdir)
        self.assertEquals(count, len(oc))


class TestOutputDirectory(TestToolsFilesystem):

    def test_no_parent_dir(self):
        odoc = os.path.join(self.tempdir, 'non-existent-parent', 'stem')
        with self.assertRaises(IOError) as ecm:
            OutputDirectory(odoc)
        e = ecm.exception
        self.assertEquals(errno.ENOENT, e.errno)

    def test_iscomplete(self):
        reldir, absdir = self.adddir('outputs/Frobnitz-HOWTO')
        o = OutputDirectory(absdir)
        self.assertFalse(o.iscomplete)
        for prop in o.expected:
            fname = getattr(o, prop, None)
            assert fname is not None
            with open(fname, 'w'):
                pass
        self.assertTrue(o.iscomplete)
        self.assertTrue('Frobnitz' in str(o))

#
# -- end of file
