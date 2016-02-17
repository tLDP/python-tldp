
from __future__ import absolute_import, division, print_function

import os
import unittest
from tempfile import NamedTemporaryFile as ntf

from tldptesttools import *

# -- SUT
from tldp.utils import makefh, which, getfileset, execute


class Test_execute(TestToolsFilesystem):

    def test_execute_returns_zero(self):
        result = execute(['true'], logdir=self.tempdir)
        self.assertEqual(0, result)

    def test_execute_returns_nonzero(self):
        result = execute(['false'], logdir=self.tempdir)
        self.assertEqual(1, result)

    def test_execute_exception_when_logdir_none(self):
        with self.assertRaises(Exception) as ecm:
            execute(['true'], logdir=None)
        e = ecm.exception
        self.assertTrue('Missing' in e.message)

    def test_execute_exception_when_logdir_enoent(self):
        logdir = os.path.join(self.tempdir, 'nonexistent-directory')
        with self.assertRaises(IOError) as ecm:
            execute(['true'], logdir=logdir)
        e = ecm.exception
        self.assertTrue('nonexistent' in e.filename)


class Test_which(unittest.TestCase):

    def test_good_which_python(self):
        python = which('python')
        self.assertIsInstance(python, str)
        self.assertTrue(os.path.isfile(python))
        qualified_python = which(python)
        self.assertEqual(python, qualified_python)

    def test_bad_silly_name(self):
        silly = which('silliest-executable-name-which-may-yet-be-possible')
        self.assertIsNone(silly)

    def test_fq_executable(self):
        f = ntf(prefix='tldp-which-test', delete=False)
        f.close()
        notfound = which(f.name)
        self.assertIsNone(notfound)
        os.chmod(f.name, 0755)
        found = which(f.name)
        self.assertEqual(f.name, found)
        os.unlink(f.name)


class Test_getfileset(unittest.TestCase):

    def test_getfileset(self):
        here = os.path.dirname(os.path.abspath(__file__))
        me = os.path.join('.', os.path.basename(__file__))
        self.assertTrue(me in getfileset(here))


class Test_makefh(unittest.TestCase):

    def test_makefh(self):
        f = ntf(prefix='tldp-makefh-openfile-test-', delete=False)
        # fprime = makefh(f.file)
        # self.assertIs(f, fprime)
        # del fprime
        f.close()
        fprime = makefh(f.name)
        self.assertIs(f.name, fprime.name)
        os.unlink(f.name)

#
# -- end of file
