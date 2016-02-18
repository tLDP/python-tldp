
from __future__ import absolute_import, division, print_function

import os
import uuid
import unittest
from tempfile import NamedTemporaryFile as ntf

from tldptesttools import TestToolsFilesystem

# -- SUT
from tldp.utils import makefh, which, execute
from tldp.utils import statfiles


class Test_execute(TestToolsFilesystem):

    def test_execute_returns_zero(self):
        exe = which ('true')
        result = execute([exe], logdir=self.tempdir)
        self.assertEqual(0, result)

    def test_execute_returns_nonzero(self):
        exe = which ('false')
        result = execute([exe], logdir=self.tempdir)
        self.assertEqual(1, result)

    def test_execute_exception_when_logdir_none(self):
        exe = which ('true')
        with self.assertRaises(Exception) as ecm:
            execute([exe], logdir=None)
        e = ecm.exception
        self.assertTrue('Missing' in e.message)

    def test_execute_exception_when_logdir_enoent(self):
        exe = which ('true')
        logdir = os.path.join(self.tempdir, 'nonexistent-directory')
        with self.assertRaises(IOError) as ecm:
            execute([exe], logdir=logdir)
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


class Test_statfiles(unittest.TestCase):

    def test_statfiles_dir_rel(self):
        here = os.path.dirname(os.path.abspath(__file__))
        statinfo = statfiles(here, relative=here)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(os.path.basename(__file__) in statinfo)

    def test_statfiles_dir_abs(self):
        here = os.path.dirname(os.path.abspath(__file__))
        statinfo = statfiles(here)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(__file__ in statinfo)

    def test_statfiles_file_rel(self):
        here = os.path.dirname(os.path.abspath(__file__))
        statinfo = statfiles(__file__, relative=here)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(os.path.basename(__file__) in statinfo)

    def test_statfiles_file_abs(self):
        statinfo = statfiles(__file__)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(__file__ in statinfo)

    def test_statfiles_nonexistent_file(self):
        here = os.path.dirname(os.path.abspath(__file__))
        this = os.path.join(here, str(uuid.uuid4()))
        statinfo = statfiles(this)
        self.assertIsInstance(statinfo, dict)
        self.assertEquals(0, len(statinfo))


class Test_att_statinfo(unittest.TestCase):

    def test_max_mtime(self):
        pass


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
